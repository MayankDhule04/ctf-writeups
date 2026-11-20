<?php
/**
 * This code is intentionally vulnerable to command injection for the purpose of a CTF challenge.
 * See challenge.yml and README.md for more details on the challenge and how to exploit it.
 * 
 * If you have just read this file from within the challenge, you won't find the flag here.
 */

function vuln_check($ip) {
    // These comments can be adjusted to make the code more or less vulnerable,
    // depending on the desired level of difficulty for the challenge.

    if (!vuln_is_ip($ip)) return true;
    if (vuln_contains($ip, ' ')) return true;
    if (vuln_contains($ip, '/')) return true;
    if (vuln_contains($ip, '"')) return true;
    if (vuln_contains($ip, "'")) return true;
    // if (vuln_contains($ip, 'flag.txt')) return true;
    if (vuln_contains($ip, 'cat')) return true;
    // if (vuln_contains($ip, 'tmp')) return true;
    return false;
}

// Check if the input contains a valid IP address
function vuln_is_ip($ip) {
    // Return true if the input contains any valid IP address (IPv4 or IPv6)
    $hay = strtolower($ip);
    // Find candidate IP-like substrings
    preg_match_all('/\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b|\b[0-9a-f:]+\b/i', $hay, $matches);
    if (empty($matches[0])) return false;
    foreach ($matches[0] as $candidate) {
        if (filter_var($candidate, FILTER_VALIDATE_IP)) {
            return true;
        }
    }
    return false;
}

// Check if the input contains whitespace characters
function vuln_contains($ip, $contains) {
    return str_contains(strtolower($ip), $contains);
}


$executed = false;
$valid = false;
$output = '';
$submitted_host = '';

if (isset($_POST['host'])) {

    $valid = true;
    $submitted_host = $_POST['host'];

    if (vuln_check($submitted_host)) {
        $valid = false;
    } else {
        $executed = true;
        $output = shell_exec("bash -c 'ping -c 4 " . $submitted_host . "'");
        if ($output === null || $output === false) {
            $output = 'Ping could not be executed. Make sure the container has the ping command available.';
        }
    }
}


?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ping Command Injection</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0b1020;
            --panel: rgba(15, 23, 42, 0.88);
            --panel-border: rgba(148, 163, 184, 0.18);
            --text: #e2e8f0;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --accent-2: #22c55e;
            --danger: #f87171;
            --shadow: 0 24px 80px rgba(2, 6, 23, 0.5);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 32%),
                radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.12), transparent 28%),
                linear-gradient(160deg, #050816 0%, #0b1020 45%, #060912 100%);
        }

        .shell {
            width: min(960px, calc(100% - 32px));
            margin: 0 auto;
            padding: 56px 0 40px;
        }

        .hero {
            display: grid;
            gap: 16px;
            margin-bottom: 24px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            width: fit-content;
            padding: 8px 12px;
            border: 1px solid var(--panel-border);
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.62);
            color: var(--muted);
            font-size: 0.875rem;
            letter-spacing: 0.02em;
            backdrop-filter: blur(14px);
        }

        .eyebrow::before {
            content: '';
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.45);
        }

        h1 {
            margin: 0;
            font-size: clamp(2.4rem, 5vw, 4.5rem);
            line-height: 0.95;
            letter-spacing: -0.05em;
            max-width: 10ch;
        }

        .lede {
            margin: 0;
            max-width: 60ch;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .card {
            display: grid;
            gap: 22px;
            padding: 28px;
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            background: var(--panel);
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
        }

        form {
            display: grid;
            gap: 14px;
        }

        label {
            font-size: 0.95rem;
            color: var(--muted);
        }

        .input-row {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 12px;
        }

        input[type="text"] {
            width: 100%;
            padding: 16px 18px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 16px;
            background: rgba(2, 6, 23, 0.65);
            color: var(--text);
            font: inherit;
            outline: none;
            transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
        }

        input[type="text"]:focus {
            border-color: rgba(56, 189, 248, 0.8);
            box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.12);
        }

        button {
            border: 0;
            border-radius: 16px;
            padding: 16px 22px;
            background: linear-gradient(135deg, var(--accent), #0ea5e9);
            color: #02111f;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
            transition: transform 160ms ease, filter 160ms ease;
        }

        button:hover {
            transform: translateY(-1px);
            filter: brightness(1.05);
        }

        .meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            color: var(--muted);
            font-size: 0.9rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            padding: 7px 11px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(15, 23, 42, 0.6);
        }

        .result {
            display: grid;
            gap: 10px;
        }

        .result h2 {
            margin: 0;
            font-size: 1.05rem;
            color: #f8fafc;
        }

        pre {
            margin: 0;
            padding: 18px;
            overflow: auto;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(2, 6, 23, 0.78);
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .error {
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid rgba(248, 113, 113, 0.28);
            background: rgba(127, 29, 29, 0.28);
            color: #fecaca;
        }

        @media (max-width: 720px) {
            .shell {
                width: min(100% - 20px, 960px);
                padding: 20px 0 28px;
            }

            .card {
                padding: 20px;
                border-radius: 20px;
            }

            .input-row {
                grid-template-columns: 1fr;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <h1>Don't Ping that Cat! (L3)</h1>
        </section>

        <section class="card">
            <form method="POST">
                <label for="host">Target host</label>
                <div class="input-row">
                    <input
                        type="text"
                        id="host"
                        name="host"
                        placeholder="e.g. 8.8.8.8"
                        value="<?php echo htmlspecialchars($submitted_host); ?>"
                        required>
                    <button type="submit">Ping</button>
                </div>
            </form>
            <?php if ($valid && $executed): ?>
                <div class="result">
                    <h2>Ping Output</h2>
                    <pre><?php echo htmlspecialchars($output); ?></pre>
                </div>
            <?php elseif (isset($_POST['host']) && !$valid): ?>
                <div class="error">Invalid input. Trying to be sneaky?</div>
            <?php endif; ?>
        </section>
    </main>
</body>
</html>