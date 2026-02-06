class LuasScheduleCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static getConfigElement() {
    return document.createElement('luas-schedule-card-editor');
  }

  static getStubConfig() {
    return {
      entity: '',
      view_type: 'full',
      max_trams: 5,
      show_inbound: true,
      show_outbound: true,
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
    this._config = {
      view_type: 'full',
      max_trams: 5,
      show_inbound: true,
      show_outbound: true,
      ...config,
    };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _getBaseEntity() {
    // Extract the stop name from the entity (e.g., sensor.cherrywood_inbound_next -> cherrywood)
    const entity = this._config.entity;
    const match = entity.match(/sensor\.(.+?)_(inbound|outbound)_next/);
    if (match) {
      return match[1];
    }
    // If it's a status entity
    const statusMatch = entity.match(/sensor\.(.+?)_status/);
    if (statusMatch) {
      return statusMatch[1];
    }
    return entity.split('.')[1];
  }

  _render() {
    if (!this._hass || !this._config) return;

    const baseName = this._getBaseEntity();
    const inboundEntity = `sensor.${baseName}_inbound_next`;
    const outboundEntity = `sensor.${baseName}_outbound_next`;
    const statusEntity = `sensor.${baseName}_status`;

    const inboundState = this._hass.states[inboundEntity];
    const outboundState = this._hass.states[outboundEntity];
    const statusState = this._hass.states[statusEntity];

    const stopName = inboundState?.attributes?.stop_name ||
      outboundState?.attributes?.stop_name ||
      baseName.replace(/_/g, ' ');

    const statusMessage = statusState?.state || 'Unknown';
    const inboundTrams = inboundState?.attributes?.all_trams || [];
    const outboundTrams = outboundState?.attributes?.all_trams || [];

    const maxTrams = this._config.max_trams || 5;
    const viewType = this._config.view_type || 'full';
    const showInbound = this._config.show_inbound !== false;
    const showOutbound = this._config.show_outbound !== false;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --luas-primary-color: var(--primary-color, #03a9f4);
          --luas-text-color: var(--primary-text-color, #fff);
          --luas-secondary-text: var(--secondary-text-color, #aaa);
          --luas-bg-color: var(--card-background-color, #1c1c1c);
          --luas-border-radius: var(--ha-card-border-radius, 12px);
        }
        
        .card {
          background: var(--luas-bg-color);
          border-radius: var(--luas-border-radius);
          padding: 16px;
          font-family: var(--paper-font-body1_-_font-family, 'Roboto', sans-serif);
        }
        
        .header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }
        
        .tram-icon {
          font-size: 28px;
        }
        
        .title {
          font-size: 18px;
          font-weight: 500;
          color: var(--luas-text-color);
        }
        
        .status {
          font-size: 12px;
          color: var(--luas-secondary-text);
          margin-top: 2px;
        }
        
        .direction {
          margin-bottom: 16px;
        }
        
        .direction:last-child {
          margin-bottom: 0;
        }
        
        .direction-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          color: var(--luas-text-color);
          margin-bottom: 8px;
          padding-bottom: 4px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .direction-icon {
          font-size: 16px;
        }
        
        .tram-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .tram-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
        }
        
        .tram-destination {
          font-size: 14px;
          color: var(--luas-text-color);
        }
        
        .tram-time {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .tram-due {
          font-size: 14px;
          font-weight: 600;
          color: var(--luas-primary-color);
          min-width: 60px;
          text-align: right;
        }
        
        .tram-due.due-now {
          color: #4caf50;
          animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        
        .tram-arrival {
          font-size: 12px;
          color: var(--luas-secondary-text);
          min-width: 45px;
          text-align: right;
        }
        
        .no-trams {
          font-size: 14px;
          color: var(--luas-secondary-text);
          font-style: italic;
          padding: 8px 0;
        }
        
        /* Compact View Styles */
        .compact .direction {
          margin-bottom: 8px;
        }
        
        .compact .tram-item {
          padding: 6px 10px;
        }
        
        .compact .tram-destination {
          font-size: 13px;
        }
        
        .compact .tram-due {
          font-size: 13px;
        }
      </style>
      
      <ha-card>
        <div class="card ${viewType === 'compact' ? 'compact' : ''}">
          <div class="header">
            <span class="tram-icon">🚃</span>
            <div>
              <div class="title">${this._capitalizeWords(stopName)}</div>
              <div class="status">${statusMessage}</div>
            </div>
          </div>
          
          ${showInbound ? this._renderDirection('Inbound', '⬆️', inboundTrams, maxTrams, viewType) : ''}
          ${showOutbound ? this._renderDirection('Outbound', '⬇️', outboundTrams, maxTrams, viewType) : ''}
        </div>
      </ha-card>
    `;
  }

  _renderDirection(name, icon, trams, maxTrams, viewType) {
    const displayTrams = trams.slice(0, maxTrams);

    if (displayTrams.length === 0) {
      return `
        <div class="direction">
          <div class="direction-header">
            <span class="direction-icon">${icon}</span>
            ${name}
          </div>
          <div class="no-trams">No trams scheduled</div>
        </div>
      `;
    }

    const tramsHtml = displayTrams.map(tram => {
      const isDue = tram.due === 'DUE';
      return `
        <div class="tram-item">
          <span class="tram-destination">${tram.destination}</span>
          <div class="tram-time">
            <span class="tram-due ${isDue ? 'due-now' : ''}">${tram.due}</span>
            ${viewType === 'full' ? `<span class="tram-arrival">${tram.arrival_time}</span>` : ''}
          </div>
        </div>
      `;
    }).join('');

    return `
      <div class="direction">
        <div class="direction-header">
          <span class="direction-icon">${icon}</span>
          ${name}
        </div>
        <div class="tram-list">
          ${tramsHtml}
        </div>
      </div>
    `;
  }

  _capitalizeWords(str) {
    return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  getCardSize() {
    return 3;
  }
}

// Card Editor for visual configuration
class LuasScheduleCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    // Re-render to populate entity dropdown
    if (this.shadowRoot.innerHTML) {
      this._updateEntityDropdown();
    }
  }

  _getLuasStops() {
    // Find all Luas entities by checking for Luas-specific attributes
    if (!this._hass) return [];

    const stops = new Map();

    Object.keys(this._hass.states).forEach(entityId => {
      const state = this._hass.states[entityId];

      // Check for Luas-specific attributes (stop_code or all_trams)
      // These are unique to our Luas integration
      if (!state?.attributes?.stop_code && !state?.attributes?.all_trams) {
        return; // Not a Luas entity
      }

      // Extract stop name from entity ID
      const match = entityId.match(/^sensor\.(.+?)_(inbound_next|outbound_next|status)$/);
      if (!match) return;

      const stopKey = match[1];
      const sensorType = match[2];
      const displayName = state.attributes.stop_name ||
        stopKey.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

      if (!stops.has(stopKey)) {
        stops.set(stopKey, {
          name: stopKey,
          displayName: displayName,
          entities: []
        });
      }
      stops.get(stopKey).entities.push({
        id: entityId,
        type: sensorType
      });
    });

    return Array.from(stops.values()).sort((a, b) =>
      a.displayName.localeCompare(b.displayName)
    );
  }

  _updateEntityDropdown() {
    const select = this.shadowRoot.getElementById('entity');
    if (!select) return;

    // Only update the value, don't rebuild options (which causes selection loss)
    const currentValue = this._config.entity || '';
    if (select.value !== currentValue) {
      select.value = currentValue;
    }
  }

  _render() {
    const stops = this._getLuasStops();
    const currentValue = this._config.entity || '';

    let entityOptions = '<option value="">-- Select a Luas Stop --</option>';
    stops.forEach(stop => {
      const mainEntity = stop.entities.find(e => e.type === 'inbound_next') || stop.entities[0];
      if (mainEntity) {
        const selected = currentValue === mainEntity.id ? 'selected' : '';
        entityOptions += `<option value="${mainEntity.id}" ${selected}>${stop.displayName}</option>`;
      }
    });

    this.shadowRoot.innerHTML = `
      <style>
        .editor {
          padding: 16px;
        }
        .row {
          margin-bottom: 16px;
        }
        label {
          display: block;
          font-weight: 500;
          margin-bottom: 4px;
          color: var(--primary-text-color);
        }
        select, input[type="number"] {
          width: 100%;
          padding: 10px;
          border: 1px solid var(--divider-color, #444);
          border-radius: 6px;
          background: var(--card-background-color, #1c1c1c);
          color: var(--primary-text-color, #fff);
          box-sizing: border-box;
          font-size: 14px;
        }
        select:focus, input:focus {
          outline: none;
          border-color: var(--primary-color, #03a9f4);
        }
        .checkbox-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .checkbox-row input {
          width: 18px;
          height: 18px;
          accent-color: var(--primary-color, #03a9f4);
        }
        .checkbox-row label {
          margin-bottom: 0;
        }
        .hint {
          font-size: 12px;
          color: var(--secondary-text-color, #888);
          margin-top: 4px;
        }
        .no-stops {
          padding: 12px;
          background: var(--warning-color, #ff9800);
          border-radius: 6px;
          color: #000;
          font-size: 13px;
        }
      </style>
      <div class="editor">
        ${stops.length === 0 ? `
          <div class="no-stops">
            ⚠️ No Luas stops configured yet. Add a stop via Settings → Devices & Services → Dublin Luas Schedule.
          </div>
        ` : `
          <div class="row">
            <label>Luas Stop</label>
            <select id="entity">
              ${entityOptions}
            </select>
          </div>
        `}
        <div class="row">
          <label>View Type</label>
          <select id="view_type">
            <option value="full" ${this._config.view_type === 'full' ? 'selected' : ''}>Full Schedule (with arrival times)</option>
            <option value="compact" ${this._config.view_type === 'compact' ? 'selected' : ''}>Compact View</option>
          </select>
        </div>
        <div class="row">
          <label>Max Trams to Show</label>
          <input type="number" id="max_trams" min="1" max="10" 
                 value="${this._config.max_trams || 5}">
          <div class="hint">Per direction (1-10)</div>
        </div>
        <div class="row checkbox-row">
          <input type="checkbox" id="show_inbound" 
                 ${this._config.show_inbound !== false ? 'checked' : ''}>
          <label for="show_inbound">Show Inbound</label>
        </div>
        <div class="row checkbox-row">
          <input type="checkbox" id="show_outbound" 
                 ${this._config.show_outbound !== false ? 'checked' : ''}>
          <label for="show_outbound">Show Outbound</label>
        </div>
      </div>
    `;

    // Add event listeners
    const entitySelect = this.shadowRoot.getElementById('entity');
    if (entitySelect) {
      entitySelect.addEventListener('change', (e) => {
        this._updateConfig('entity', e.target.value);
      });
    }
    this.shadowRoot.getElementById('view_type').addEventListener('change', (e) => {
      this._updateConfig('view_type', e.target.value);
    });
    this.shadowRoot.getElementById('max_trams').addEventListener('change', (e) => {
      this._updateConfig('max_trams', parseInt(e.target.value));
    });
    this.shadowRoot.getElementById('show_inbound').addEventListener('change', (e) => {
      this._updateConfig('show_inbound', e.target.checked);
    });
    this.shadowRoot.getElementById('show_outbound').addEventListener('change', (e) => {
      this._updateConfig('show_outbound', e.target.checked);
    });
  }

  _updateConfig(key, value) {
    this._config = { ...this._config, [key]: value };
    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

// Register the card and editor
customElements.define('luas-schedule-card', LuasScheduleCard);
customElements.define('luas-schedule-card-editor', LuasScheduleCardEditor);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'luas-schedule-card',
  name: 'Luas Schedule Card',
  description: 'A custom card to display Dublin Luas tram schedules',
  preview: true,
});

console.info('%c LUAS-SCHEDULE-CARD %c v1.2.0 ',
  'color: white; background: #03a9f4; font-weight: bold;',
  'color: #03a9f4; background: white; font-weight: bold;'
);
