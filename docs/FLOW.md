# Print Job Flow

## Flujo Completo de un Print Job

```mermaid
flowchart TB
    subgraph CREATION["1. CREACIÓN DEL PRINT JOB"]
        A1["POST /print-jobs"]
        A2["CreatePrintJobUseCase"]
        A3["PrintJob entity"]
        A1 --> A2 --> A3
        A3 --> DB1[("DB: print_jobs<br/>status='pending'")]
    end

    subgraph WORKER["2. WORKER PROCESAMIENTO"]
        W1["PrintWorker<br/>(poll cada 5s)"]
        W2["_get_next_pending_job()"]
        W3["Lock job<br/>processing_since=now"]
        W1 --> W2 --> W3
    end

    subgraph RESOLUTION["3. RESOLUCIÓN"]
        R1["PrinterRepository<br/>get_printer_for_channel()"]
        R2["PrintJob.get_template()"]
        R3["Query Channel<br/>→ template_id"]
        R4["Fetch Template"]
        R1 --> DB2[("DB: printers<br/>printer_channels<br/>channels")]
        R2 --> R3 --> R4
        R3 --> DB3[("DB: channels<br/>templates")]
    end

    subgraph RENDER["4. RENDERIZADO"]
        RH1["PrintJob.render()"]
        RH2{template?}
        RH2A{file_path<br/>extension?}
        RH3["<b>.zpl</b><br/>→ _render_label()"]
        RH4["<b>.html</b><br/>→ _render_remito()"]
        RH5["<b>sin template</b><br/>→ _get_pdf_from_payload()"]
        RH6["Jinja2 template"]
        RH7["Jinja2 + WeasyPrint<br/>+ BarcodeService"]
        RH1 --> RH2
        RH2 -->|"template"| RH2A
        RH2 -->|"sin template<br/>(channel 2)"| RH5 --> PDF2[("PDF bytes")]
        RH2A -->|".zpl"| RH3 --> RH6 --> ZPL[("ZPL bytes")]
        RH2A -->|".html"| RH4 --> RH7 --> PDF[("PDF bytes")]
        
        subgraph DATA["Parse payload"]
            D1["get_render_data_label()"]
            D2["get_render_data_remito()"]
            D3["pdf_base64 / pdf_url / pdf_path"]
            RH3 --> D1
            RH4 --> D2
            RH5 --> D3
        end
    end

    subgraph SEND["5. ENVÍO A IMPRESORA"]
        S1["_send_to_printer()<br/>(placeholder)"]
        S2["Update job status<br/>status='printed'"]
        S1 --> S2 --> DB4[("DB: print_jobs<br/>updated")]
    end

    DB1 --> WORKER
    WORKER --> RESOLUTION
    RESOLUTION --> RENDER
    RENDER --> SEND
    
    style CREATION fill:#e1f5fe
    style WORKER fill:#fff3e0
    style RESOLUTION fill:#e8f5e9
    style RENDER fill:#fce4ec
    style SEND fill:#f3e5f5
```

---

## Descripción del Flujo

| Paso | Componente | Descripción |
|------|-----------|-------------|
| **1** | API → UseCase → Entity | Se crea el PrintJob en la DB con status "pending" |
| **2** | Worker poll | El worker hace polling cada 5 segundos buscando jobs pending |
| **3** | Resolución | Se busca en la DB la impresora y el template asociados al channel |
| **4** | Renderizado | Se decide por extensión (.zpl = label, .html = remito/PDF) |
| **5** | Envío | Se envía a la impresora y se actualiza el status |

---

## Entidades Principales

| Entidad | Tabla DB | Relación |
|---------|----------|----------|
| **PrintJob** | `print_jobs` | Datos del trabajo |
| **Channel** | `channels` | Define tipo de documento |
| **Template** | `templates` | Archivo (file_path) a usar |
| **Printer** | `printers` | Impresora física |
| **PrinterChannel** | `printer_channels` | Relación many-to-many |

---

## Decisión de Template

```
print_job.render()
    │
    ├── template = get_template()
    │       │
    │       └── Query: Channel → template_id → Template
    │
    ├── if not template (channel sin template, ej. channel 2):
    │       └── _get_pdf_from_payload() → PDF bytes
    │             (pdf_base64 | pdf_url | pdf_path/ftp_filename)
    │
    ├── elif template.file_path.endswith('.zpl'):
    │       └── _render_label() → ZPL bytes
    │
    └── elif template.file_path.endswith('.html'):
            └── _render_remito() → PDF bytes (via WeasyPrint)
```

### Channel 2: PDF pre-generados

Para channels sin template (ej. channel 2), el payload debe contener una de:

| Campo | Descripción |
|-------|-------------|
| `pdf_base64` | PDF codificado en base64 |
| `pdf_url` | URL HTTP/HTTPS para descargar el PDF |
| `pdf_path` / `ftp_filename` | Ruta local (absoluta o relativa a `/app/infrastructure/data/pdfs`) |

---

## Decisión de Impresora

```
Worker._process_one_job()
    │
    └── printer = printer_repo.get_printer_for_channel(channel)
            │
            └── Join: Printer → PrinterChannel → Channel
                      WHERE channel_number = {channel}
```
