const API_CHANNELS = '/channels';
const API_PRINTERS = '/printers';
const API_PRINTERS_DISCOVER = '/printers/discover';
const API_TEMPLATES = '/templates';
const REFRESH_INTERVAL = 30000;

let allChannels = [];
let allTemplates = [];

// Tab switching
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
            document.getElementById(`${tabName}-section`).classList.add('active');
            if (tabName === 'channels') loadChannels();
            else if (tabName === 'printers') loadPrinters();
        });
    });
    
    loadChannels();
    loadPrinters();
    setInterval(() => {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        if (activeTab === 'channels') loadChannels();
        else if (activeTab === 'printers') loadPrinters();
    }, REFRESH_INTERVAL);
});

// ============ CHANNELS ============

async function loadChannels() {
    try {
        const response = await fetch(API_CHANNELS);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        allChannels = await response.json();
        renderChannels(allChannels);
        setConnectionStatus(true);
    } catch (error) {
        console.error('Error cargando channels:', error);
        document.getElementById('channels-body').innerHTML = 
            `<tr><td colspan="5" class="error">Error: ${error.message}</td></tr>`;
        setConnectionStatus(false);
    }
}

function renderChannels(channels) {
    const tbody = document.getElementById('channels-body');
    if (!channels || channels.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No hay channels configurados</td></tr>';
        return;
    }
    
    tbody.innerHTML = channels.map(c => {
        const activeClass = c.is_active ? 'active' : 'inactive';
        const templateName = allTemplates.find(t => t.id === c.template_id)?.name || '-';
        return `
            <tr class="${activeClass}">
                <td>${c.id}</td>
                <td><strong>${c.channel_number}</strong></td>
                <td>${c.description || '-'}</td>
                <td>${templateName}</td>
                <td><span class="status-badge ${activeClass}">${c.is_active ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    <button onclick="editChannel(${c.id}, ${c.channel_number}, '${c.description || ''}', ${c.is_active}, ${c.template_id})" class="btn-edit">Editar</button>
                    <button onclick="deleteChannel(${c.id})" class="btn-delete">Eliminar</button>
                </td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('last-update').textContent = 
        `Última actualización: ${new Date().toLocaleTimeString()}`;
}

async function showChannelModal(id = null, channelNumber = '', description = '', isActive = true, templateId = null) {
    document.getElementById('channel-modal').style.display = 'flex';
    document.getElementById('channel-modal-title').textContent = id ? 'Editar Channel' : 'Nuevo Channel';
    document.getElementById('channel-id').value = id || '';
    document.getElementById('channel-number').value = channelNumber;
    document.getElementById('channel-description').value = description;
    document.getElementById('channel-active').checked = isActive;
    document.getElementById('channel-number').disabled = !!id;
    
    // Cargar templates
    const templateSelect = document.getElementById('channel-template');
    templateSelect.innerHTML = '<option value="">-- Seleccionar --</option>';
    
    try {
        const response = await fetch(API_TEMPLATES);
        allTemplates = await response.json();
        allTemplates.forEach(t => {
            const option = document.createElement('option');
            option.value = t.id;
            option.textContent = t.name;
            if (templateId && t.id === templateId) {
                option.selected = true;
            }
            templateSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando templates:', error);
    }
    
    // Si es nuevo, hacer required el template
    templateSelect.required = !id;
}

function closeChannelModal() {
    document.getElementById('channel-modal').style.display = 'none';
    document.getElementById('channel-form').reset();
}

function editChannel(id, channelNumber, description, isActive, templateId) {
    showChannelModal(id, channelNumber, description, isActive, templateId);
}

async function deleteChannel(id) {
    if (!confirm('¿Eliminar este channel?')) return;
    try {
        const response = await fetch(`${API_CHANNELS}/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al eliminar');
        loadChannels();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

document.getElementById('channel-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('channel-id').value;
    const channelNumber = parseInt(document.getElementById('channel-number').value);
    const description = document.getElementById('channel-description').value || null;
    const isActive = document.getElementById('channel-active').checked;
    const templateId = parseInt(document.getElementById('channel-template').value) || null;
    
    try {
        let response;
        if (id) {
            response = await fetch(`${API_CHANNELS}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description, is_active: isActive, template_id: templateId })
            });
        } else {
            response = await fetch(API_CHANNELS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ channel_number: channelNumber, description, template_id: templateId })
            });
        }
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Error al guardar');
        }
        closeChannelModal();
        loadChannels();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// ============ PRINTERS ============

async function loadPrinters() {
    try {
        const response = await fetch(API_PRINTERS);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const printers = await response.json();
        renderPrinters(printers);
    } catch (error) {
        console.error('Error cargando impresoras:', error);
        document.getElementById('printers-body').innerHTML = 
            `<tr><td colspan="5" class="error">Error: ${error.message}</td></tr>`;
    }
}

function renderPrinters(printers) {
    const tbody = document.getElementById('printers-body');
    if (!printers || printers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No hay impresoras configuradas</td></tr>';
        return;
    }
    
    tbody.innerHTML = printers.map(p => {
        const activeClass = p.is_active ? 'active' : 'inactive';
        const channelText = p.channel_count > 0 
            ? `${p.channel_count} canal${p.channel_count > 1 ? 'es' : ''}`
            : 'Sin canales';
        
        return `
            <tr class="${activeClass}">
                <td><strong>${p.name}</strong></td>
                <td>
                    <button onclick="showPrinterChannelsModal(${p.id}, '${p.name}', ${JSON.stringify(p.channels).replace(/"/g, '&quot;')})" class="btn-link">
                        ${channelText}
                    </button>
                </td>
                <td><span class="status-badge ${activeClass}">${p.is_active ? 'Activa' : 'Inactiva'}</span></td>
                <td>
                    <button onclick="editPrinter(${p.id}, '${p.name}', ${p.is_active})" class="btn-edit">Editar</button>
                    <button onclick="deletePrinter(${p.id})" class="btn-delete">Eliminar</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Printer Modal
let discoveredPrinters = [];

async function showPrinterModal(id = null, name = '', isActive = true) {
    document.getElementById('printer-modal').style.display = 'flex';
    document.getElementById('printer-modal-title').textContent = id ? 'Editar Impresora' : 'Nueva Impresora';
    document.getElementById('printer-id').value = id || '';
    document.getElementById('printer-name').value = name || '';
    document.getElementById('printer-active').checked = isActive;
    
    // Fetch impresoras de CUPS (siempre, tanto para crear como editar)
    try {
        const response = await fetch(API_PRINTERS_DISCOVER);
        discoveredPrinters = await response.json();
        
        const select = document.getElementById('printer-select');
        select.innerHTML = '<option value="">Seleccionar impresora...</option>';
        
        if (discoveredPrinters.length === 0) {
            select.innerHTML = '<option value="">No hay impresoras en CUPS</option>';
        } else {
            discoveredPrinters.forEach(p => {
                const option = document.createElement('option');
                option.value = p.name;
                option.textContent = `${p.name} (${p.model}) - ${p.type}`;
                option.dataset.type = p.type;
                select.appendChild(option);
            });
        }
        
        // Si hay nombre guardado (edición), seleccionar la que haga match
        if (name) {
            const match = discoveredPrinters.find(p => p.name === name);
            if (match) {
                select.value = name;
            }
        }
        
        // Listener para cambio de selección
        select.onchange = (e) => {
            const selected = discoveredPrinters.find(p => p.name === e.target.value);
            if (selected) {
                document.getElementById('printer-name').value = selected.name;
            }
        };
    } catch (error) {
        console.error('Error fetching printers:', error);
    }
}

function closePrinterModal() {
    document.getElementById('printer-modal').style.display = 'none';
    document.getElementById('printer-form').reset();
}

function editPrinter(id, name, isActive) {
    showPrinterModal(id, name, isActive);
}

async function deletePrinter(id) {
    if (!confirm('¿Eliminar esta impresora?')) return;
    try {
        const response = await fetch(`${API_PRINTERS}/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al eliminar');
        loadPrinters();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

document.getElementById('printer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('printer-id').value;
    const name = document.getElementById('printer-name').value;
    const isActive = document.getElementById('printer-active').checked;
    
    try {
        let response;
        const body = { name, is_active: isActive };
        
        if (id) {
            response = await fetch(`${API_PRINTERS}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        } else {
            response = await fetch(API_PRINTERS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        }
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Error al guardar');
        }
        closePrinterModal();
        loadPrinters();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Printer Channels Modal
async function showPrinterChannelsModal(printerId, printerName, currentChannels) {
    document.getElementById('printer-channels-modal').style.display = 'flex';
    document.getElementById('printer-channels-modal-title').textContent = `Channels - ${printerName}`;
    document.getElementById('printer-channels-id').value = printerId;
    
    // Get all available channels
    const channelsResponse = await fetch(API_CHANNELS);
    const allChannelsData = await channelsResponse.json();
    
    const currentChannelIds = (currentChannels || []).map(c => c.channel_id);
    
    const checkboxesDiv = document.getElementById('channels-checkboxes');
    checkboxesDiv.innerHTML = allChannelsData.map(ch => `
        <label class="checkbox-item">
            <input type="checkbox" name="channel" value="${ch.id}" ${currentChannelIds.includes(ch.id) ? 'checked' : ''}>
            <span>ID:${ch.id} - ${ch.channel_number} - ${ch.description || 'Sin descripción'}</span>
        </label>
    `).join('');
    
    if (allChannelsData.length === 0) {
        checkboxesDiv.innerHTML = '<p class="empty">No hay channels disponibles. Cree primero channels en la sección Channels.</p>';
    }
}

function closePrinterChannelsModal() {
    document.getElementById('printer-channels-modal').style.display = 'none';
    document.getElementById('channels-checkboxes').innerHTML = '';
}

document.getElementById('printer-channels-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const printerId = document.getElementById('printer-channels-id').value;
    
    const selectedChannels = Array.from(document.querySelectorAll('input[name="channel"]:checked'))
        .map(cb => parseInt(cb.value));
    
    try {
        const response = await fetch(`${API_PRINTERS}/${printerId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel_ids: selectedChannels })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Error al guardar');
        }
        closePrinterChannelsModal();
        loadPrinters();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

function setConnectionStatus(online) {
    const dot = document.getElementById('connection-status');
    dot.className = 'status-dot ' + (online ? 'online' : 'offline');
    dot.title = online ? 'Conectado' : 'Sin conexión';
}
