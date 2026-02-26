const API_URL = '/printers';
const REFRESH_INTERVAL = 30000; // 30 seconds

let isOnline = true;

function formatPrinterType(type) {
    const types = {
        'zebra': 'Zebra (ZPL)',
        'laser': 'Láser (PDF)'
    };
    return types[type] || type;
}

function renderPrinters(printers) {
    const tbody = document.getElementById('printers-body');
    
    if (!printers || printers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No hay impresoras configuradas</td></tr>';
        return;
    }

    tbody.innerHTML = printers.map(p => {
        const activeClass = (p.printer_is_active && p.channel_is_active) ? 'active' : 'inactive';
        const statusText = (p.printer_is_active && p.channel_is_active) ? 'Activa' : 'Inactiva';
        
        return `
            <tr class="${activeClass}">
                <td>${p.printer_name}</td>
                <td>${formatPrinterType(p.printer_type)}</td>
                <td>${p.channel}</td>
                <td>${p.description || '-'}</td>
                <td>
                    <span class="status-badge ${activeClass}">${statusText}</span>
                </td>
            </tr>
        `;
    }).join('');

    document.getElementById('last-update').textContent = 
        `Última actualización: ${new Date().toLocaleTimeString()}`;
}

function showError(message) {
    const tbody = document.getElementById('printers-body');
    tbody.innerHTML = `<tr><td colspan="5" class="error">Error: ${message}</td></tr>`;
    setConnectionStatus(false);
}

function setConnectionStatus(online) {
    isOnline = online;
    const dot = document.getElementById('connection-status');
    dot.className = 'status-dot ' + (online ? 'online' : 'offline');
    dot.title = online ? 'Conectado' : 'Sin conexión';
}

async function loadPrinters() {
    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const printers = await response.json();
        renderPrinters(printers);
        setConnectionStatus(true);
        
    } catch (error) {
        console.error('Error cargando impresoras:', error);
        showError(error.message);
    }
}

function init() {
    loadPrinters();
    
    // Auto-refresh
    setInterval(loadPrinters, REFRESH_INTERVAL);
}

document.addEventListener('DOMContentLoaded', init);
