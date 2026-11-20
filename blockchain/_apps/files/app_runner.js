document.addEventListener("DOMContentLoaded", function() {

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // 1. Fetch & Render Active Keys
  async function loadKeys() {
    var tbody = document.getElementById('keys-tbody');
    if (!tbody) return;

    try {
      var res = await fetch('/api/v1/keys');
      var data = await res.json();
      
      if (res.ok && data.ok && Array.isArray(data.keys)) {
        if (data.keys.length === 0) {
          tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:1rem; color:hsl(var(--muted-foreground))">No active keys generated yet.</td></tr>';
          return;
        }

        tbody.innerHTML = '';
        data.keys.forEach(function(k) {
          var tr = document.createElement('tr');
          tr.className = 'key-table-row';
          
          var roleBadge = '<span class="badge-tag badge-encrypted" style="background:#f1f5f9; color:#475569; border-color:#cbd5e1;">GUEST</span>';
          if (k.role === 'deployer') {
            roleBadge = '<span class="badge-tag badge-ready" style="background:#dcfce7; color:#166534; border-color:#bbf7d0;">DEPLOYER</span>';
          } else if (k.role === 'admin' || k.role === 'root') {
            roleBadge = '<span class="badge-tag badge-pid" style="background:#e0f2fe; color:#0369a1; border-color:#bae6fd;">' + escapeHtml(k.role.toUpperCase()) + '</span>';
          }

          tr.innerHTML = '<td><strong>' + escapeHtml(k.name) + '</strong><br><span style="color:hsl(var(--muted-foreground)); font-size:10px;">' + escapeHtml(k.description || 'No description') + '</span></td>' +
                         '<td><code style="color:hsl(var(--accent));">' + escapeHtml(k.key_prefix) + '</code></td>' +
                         '<td>' + roleBadge + '</td>';
          tbody.appendChild(tr);
        });
      } else {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:1rem; color:#991b1b;">Failed to load registered keys.</td></tr>';
      }
    } catch (e) {
      tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:1rem; color:#991b1b;">Connection error loading keys.</td></tr>';
    }
  }

  loadKeys();

  // 2. Key Modal Elements
  var keyModal = document.getElementById('key-modal');
  var keyDisplay = document.getElementById('modal-key-display');
  var roleDisplay = document.getElementById('modal-role-display');
  var closeModalBtn = document.getElementById('close-modal-btn');
  var closeModalCross = document.getElementById('close-modal-cross');
  var pasteKeyBtn = document.getElementById('modal-use-key-btn');
  var generatedKeyString = '';

  function openKeyModal(keyObj) {
    if (!keyModal) return;
    generatedKeyString = keyObj.key;
    if (keyDisplay) keyDisplay.textContent = keyObj.key;
    if (roleDisplay) {
      roleDisplay.textContent = keyObj.role ? keyObj.role.toUpperCase() : 'GUEST';
      if (keyObj.role === 'deployer') {
        roleDisplay.style.color = '#166534';
      } else {
        roleDisplay.style.color = 'hsl(var(--primary))';
      }
    }
    keyModal.style.display = 'flex';
  }

  function closeKeyModal() {
    if (keyModal) keyModal.style.display = 'none';
  }

  if (closeModalBtn) closeModalBtn.addEventListener('click', closeKeyModal);
  if (closeModalCross) closeModalCross.addEventListener('click', closeKeyModal);
  if (pasteKeyBtn) {
    pasteKeyBtn.addEventListener('click', function() {
      var deployAuthInput = document.getElementById('deploy-auth');
      if (deployAuthInput && generatedKeyString) {
        deployAuthInput.value = generatedKeyString;
      }
      closeKeyModal();
    });
  }

  // 3. Handle Key Generation Form Submit
  var keyForm = document.getElementById('key-form');
  if (keyForm) {
    keyForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      var nameInput = document.getElementById('key-name');
      var descInput = document.getElementById('key-desc');

      var payload = {
        name: nameInput.value.trim(),
        description: descInput.value.trim()
        // Note: The UI only sends name & description.
        // Attacker intercepts via Burp and injects "role": "deployer" (Mass Assignment)
      };

      try {
        var res = await fetch('/api/v1/keys', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        var data = await res.json();
        if (res.ok && data.ok && data.key) {
          openKeyModal(data.key);
          nameInput.value = '';
          descInput.value = '';
          loadKeys();
        } else {
          alert("Key generation error: " + (data.error || "Unknown server error"));
        }
      } catch (err) {
        alert("Network error occurred while generating key.");
      }
    });
  }

  // 4. Handle Blueprint Template Loading
  var loadTemplateBtn = document.getElementById('load-template-btn');
  var templateSelect = document.getElementById('template-select');
  var deployYamlTextarea = document.getElementById('deploy-yaml');

  if (loadTemplateBtn && templateSelect && deployYamlTextarea) {
    loadTemplateBtn.addEventListener('click', function() {
      var selected = templateSelect.value;
      var editorFilename = document.getElementById('editor-filename');
      if (selected === 'diagnostics') {
        if (editorFilename) editorFilename.textContent = 'nano diagnostics.yaml';
        deployYamlTextarea.value = "job_name: system_diagnostics\npipeline_version: '1.0'\nenvironment: read_only\nsteps:\n  - name: ping_services\n    command: echo \"All services operational\"\n  - name: check_storage\n    command: df -h";
      } else if (selected === 'python') {
        if (editorFilename) editorFilename.textContent = 'nano python_build.yaml';
        deployYamlTextarea.value = "job_name: python_flask_service\npipeline_version: '2.1'\nenvironment: production\nsteps:\n  - name: install_dependencies\n    command: pip install -r requirements.txt\n  - name: unit_tests\n    command: pytest --verbose";
      } else if (selected === 'node') {
        if (editorFilename) editorFilename.textContent = 'nano node_worker.yaml';
        deployYamlTextarea.value = "job_name: node_microservice_worker\npipeline_version: '2.1'\nenvironment: staging\nsteps:\n  - name: build_bundle\n    command: npm run build\n  - name: integration_test\n    command: npm test";
      } else if (selected === 'settlement') {
        if (editorFilename) editorFilename.textContent = 'nano settlement.yaml';
        deployYamlTextarea.value = "job_name: escrow_multisig_settlement\npipeline_version: '3.0'\nenvironment: escrow_mainnet\nsteps:\n  - name: sync_principals\n    command: echo 'Synchronizing principals...'\n  - name: release_escrow\n    command: /usr/local/bin/escrow_release --execute --target=/var/lib/escrow/ledger.enc";
      }
    });
  }

  // 5. Handle YAML Deployment Dispatch
  var deployForm = document.getElementById('deploy-form');
  var deployResult = document.getElementById('deploy-result');

  if (deployForm && deployResult) {
    deployForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      var keyVal = document.getElementById('deploy-auth').value.trim();
      var yamlVal = deployYamlTextarea.value.trim();

      deployResult.style.display = 'block';
      deployResult.style.color = '#38bdf8';
      deployResult.textContent = "[*] Transmitting YAML specification to runner worker pool...";

      try {
        var res = await fetch('/api/v1/deploy', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + keyVal,
            'Content-Type': 'application/x-yaml'
          },
          body: yamlVal
        });

        var data = await res.json();
        if (res.ok && data.ok) {
          deployResult.style.color = '#34d399';
          deployResult.textContent = "[+] SUCCESS: Job successfully parsed and executed by worker!\n" +
                                     "--------------------------------------------------\n" +
                                     "ENGINE PARSER OUTPUT:\n" +
                                     data.parsed_output;
        } else {
          deployResult.style.color = '#f87171';
          deployResult.textContent = "[-] DISPATCH FAILED: " + (data.error || "Execution denied by runner policy.");
        }
      } catch (err) {
        deployResult.style.color = '#f87171';
        deployResult.textContent = "[!] NETWORK ERROR: Failed to communicate with runner dispatch endpoint.";
      }
    });
  }

});

  // 6. Simulate Live Metrics to make the dashboard feel alive
  setInterval(function() {
    var cpuEl = document.getElementById('metric-cpu');
    var ramEl = document.getElementById('metric-ram');
    var workersEl = document.getElementById('metric-workers');
    var timeEl = document.getElementById('metric-time');

    if (cpuEl && ramEl && workersEl) {
      // Randomize CPU between 11.0% and 24.0%
      var newCpu = (11 + Math.random() * 13).toFixed(1);
      cpuEl.textContent = newCpu + '%';

      // Randomize RAM between 4.0 GB and 4.8 GB
      var newRam = (4.0 + Math.random() * 0.8).toFixed(1);
      ramEl.textContent = newRam + ' GB / 32 GB';

      // Small chance worker count fluctuates between 3, 4, or 5
      if (Math.random() > 0.85) {
         var workers = Math.floor(Math.random() * 3) + 3; 
         workersEl.textContent = workers + ' / 16';
      }
      
      // Flash the "UPDATED: JUST NOW" text slightly to show polling
      if (timeEl) {
         timeEl.style.opacity = '0.5';
         setTimeout(() => { timeEl.style.opacity = '1'; }, 300);
      }
    }
  }, 2500); // Updates every 2.5 seconds

