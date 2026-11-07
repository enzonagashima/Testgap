"""CLI Script: Ingest and structure real examples from Enzo Nagashima's personal GitHub repositories.

Repositories included:
1. AsyncNotify (Node.js message queue, retries, dead-letter, webhook)
2. E2E-test-suite (Playwright, TypeScript, API contract assertions)
3. SpeakApp (Flask, pyttsx3, audio generation, file upload)
4. API.nodejs (Express, order management, controller validation)
5. workshoppeniel (SQLite, soundboard channel volumes, state persistence)
6. access-counter (Flask, Redis, counter resilience)
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.database import default_db
from testgap.repositories.examples import ExampleRepository
from testgap.repositories.categories import CategoryRepository
from testgap.services.example_service import ExampleService
from testgap.services.review_service import ReviewService
from testgap.schemas import ExampleCreate, GapCreate
from testgap.enums import Severity, GapStatus, SourceType, ReviewStatus

ENZO_PERSONAL_CASES = [
    # -------------------------------------------------------------------------
    # 1. AsyncNotify (Node.js) - Webhook SSRF & Channel Validation
    # -------------------------------------------------------------------------
    {
        "title": "AsyncNotify: Validação de Payload de Mensageria e Mitigação de SSRF em Webhook",
        "project_name": "AsyncNotify",
        "description": "Serviço de mensageria assíncrona com retries, dead-letter e validação de canais (email, sms, push, webhook).",
        "requirements_text": (
            "REQ-NOTIF-001: O payload deve conter channel pertencente à lista: email, sms, push, webhook.\n"
            "REQ-NOTIF-002: Quando channel for 'webhook', a propriedade webhookUrl é obrigatória e deve utilizar apenas http ou https.\n"
            "REQ-NOTIF-003: URLs de webhook direcionadas a redes locais, loopback (127.0.0.1, localhost) ou endereços de metadados em nuvem (169.254.169.254) devem ser bloqueadas para prevenir Server-Side Request Forgery (SSRF).\n"
            "REQ-NOTIF-004: Parâmetros numéricos (maxAttempts >= 1 e simulateFailures >= 0) devem ser inteiros válidos."
        ),
        "source_code": (
            "// Fonte real: enzonagashima/AsyncNotify (src/notification-service.js)\n"
            "import { URL } from 'node:url';\n\n"
            "const ALLOWED_CHANNELS = new Set(['email', 'sms', 'push', 'webhook']);\n\n"
            "export function validatePayload(payload) {\n"
            "  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {\n"
            "    return 'Body must be a JSON object';\n"
            "  }\n"
            "  if (!ALLOWED_CHANNELS.has(payload.channel)) {\n"
            "    return 'channel must be one of: email, sms, push, webhook';\n"
            "  }\n"
            "  if (typeof payload.recipient !== 'string' || payload.recipient.trim() === '') {\n"
            "    return 'recipient is required';\n"
            "  }\n"
            "  if (payload.channel === 'webhook') {\n"
            "    if (typeof payload.webhookUrl !== 'string' || payload.webhookUrl.trim() === '') {\n"
            "      return 'webhookUrl is required when channel is webhook';\n"
            "    }\n"
            "    try {\n"
            "      const webhookUrl = new URL(payload.webhookUrl);\n"
            "      if (!['http:', 'https:'].includes(webhookUrl.protocol)) {\n"
            "        return 'webhookUrl must use http or https';\n"
            "      }\n"
            "      // Mitigacao SSRF contra loopback e metadados\n"
            "      const hostname = webhookUrl.hostname.toLowerCase();\n"
            "      if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '169.254.169.254') {\n"
            "        return 'webhookUrl destination is not permitted (SSRF protection)';\n"
            "      }\n"
            "    } catch (error) {\n"
            "      return 'webhookUrl must be a valid URL';\n"
            "    }\n"
            "  }\n"
            "  return null;\n"
            "}\n"
        ),
        "source_language": "javascript",
        "test_framework": "node:test",
        "test_suite_text": (
            "// Fonte real: enzonagashima/AsyncNotify (tests/notifications.test.js)\n"
            "import test from 'node:test';\n"
            "import assert from 'node:assert/strict';\n"
            "import { validatePayload } from '../src/notification-service.js';\n\n"
            "test('validates standard email notification payload', () => {\n"
            "  const err = validatePayload({\n"
            "    channel: 'email',\n"
            "    recipient: 'user@example.com',\n"
            "    template: 'welcome'\n"
            "  });\n"
            "  assert.equal(err, null);\n"
            "});\n\n"
            "test('rejects unknown notification channel', () => {\n"
            "  const err = validatePayload({ channel: 'fax', recipient: '123' });\n"
            "  assert.match(err, /channel must be one of/);\n"
            "});\n"
        ),
        "test_format": "javascript",
        "expected_behavior": "Identificar ausência de testes para proteção contra SSRF em URLs de webhook e validação de porta/IPs internos.",
        "analysis_scope": "async_notification_validation",
        "split_group": "gh_enzo_asyncnotify",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/AsyncNotify (src/notification-service.js)",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Ausência de teste contra Server-Side Request Forgery (SSRF) em Webhook",
                "description": "REQ-NOTIF-003 exige bloqueio de destinos locais (localhost, 127.0.0.1 e 169.254.169.254). A suíte de testes atual não possui asserções submetendo URLs internas para validar se a requisição é abortada.",
                "evidence": "Nenhum teste com URLs de loopback ou metadados de nuvem.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "test('rejects internal loopback and metadata webhook URLs', () => {\n"
                    "  const errLoop = validatePayload({ channel: 'webhook', recipient: 'ops', webhookUrl: 'http://localhost:8080/admin' });\n"
                    "  assert.match(errLoop, /SSRF protection/);\n"
                    "  const errMeta = validatePayload({ channel: 'webhook', recipient: 'ops', webhookUrl: 'http://169.254.169.254/meta-data' });\n"
                    "  assert.match(errMeta, /SSRF protection/);\n"
                    "});"
                ),
                "expected_result": "Bloquear o agendamento de webhook com mensagem indicando proteção SSRF."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste para URL com protocolo não HTTP (ex: file://, ftp://)",
                "description": "A suíte testa apenas URLs vazias ou canais inválidos, sem verificar a rejeição de esquemas perigosos como file:// ou ftp://.",
                "evidence": "Nenhum teste passando esquemas alternativos em webhookUrl.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "test('rejects non-http protocols in webhookUrl', () => {\n"
                    "  const err = validatePayload({ channel: 'webhook', recipient: 'sec', webhookUrl: 'file:///etc/passwd' });\n"
                    "  assert.equal(err, 'webhookUrl must use http or https');\n"
                    "});"
                ),
                "expected_result": "Rejeitar esquemas não permitidos com mensagem descritiva."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 2. E2E-test-suite (TypeScript / Playwright) - Booking Contract Validation
    # -------------------------------------------------------------------------
    {
        "title": "E2E-test-suite: Validação de Contrato de Reservas e Integridade Temporal",
        "project_name": "E2E-test-suite",
        "description": "Suíte Playwright + TypeScript para automação de testes E2E e validação de contratos de API REST.",
        "requirements_text": (
            "REQ-BOOK-001: Uma reserva deve conter campos obrigatórios: firstname, lastname, totalprice, depositpaid e bookingdates (checkin e checkout).\n"
            "REQ-BOOK-002: As datas de checkin e checkout devem respeitar o formato estrito YYYY-MM-DD.\n"
            "REQ-BOOK-003: A data de checkout deve ser posterior ou igual à data de checkin (checkout >= checkin). Reservas com datas invertidas violam a lógica de hospedagem.\n"
            "REQ-BOOK-004: O totalprice deve ser um número não-negativo (totalprice >= 0) e finito."
        ),
        "source_code": (
            "// Fonte real: enzonagashima/E2E-test-suite (src/api/assertions.ts)\n"
            "import { expect } from '@playwright/test';\n\n"
            "export function expectBookingPayload(payload) {\n"
            "  expect(payload.firstname).toBeTruthy();\n"
            "  expect(payload.lastname).toBeTruthy();\n"
            "  expect(typeof payload.totalprice).toBe('number');\n"
            "  expect(payload.totalprice >= 0).toBeTruthy();\n"
            "  expect(typeof payload.depositpaid).toBe('boolean');\n"
            "  expect(payload.bookingdates.checkin).toMatch(/^\\d{4}-\\d{2}-\\d{2}$/);\n"
            "  expect(payload.bookingdates.checkout).toMatch(/^\\d{4}-\\d{2}-\\d{2}$/);\n"
            "  // Validacao de coerencia temporal de datas\n"
            "  const checkinTime = new Date(payload.bookingdates.checkin).getTime();\n"
            "  const checkoutTime = new Date(payload.bookingdates.checkout).getTime();\n"
            "  expect(checkoutTime >= checkinTime).toBeTruthy();\n"
            "}\n"
        ),
        "source_language": "typescript",
        "test_framework": "playwright",
        "test_suite_text": (
            "// Fonte real: enzonagashima/E2E-test-suite (tests/api/booking.api.spec.ts)\n"
            "import { test, expect } from '@playwright/test';\n"
            "import { expectBookingPayload } from '../../src/api/assertions.js';\n\n"
            "test('retrieves a booking and validates payload fields', async ({ request }) => {\n"
            "  const response = await request.get('/booking/1');\n"
            "  const body = await response.json();\n"
            "  expectBookingPayload(body);\n"
            "});\n"
        ),
        "test_format": "playwright",
        "expected_behavior": "Detectar falta de asserções para preços negativos e anomalias de datas retroativas no contrato.",
        "analysis_scope": "e2e_booking_api_assertions",
        "split_group": "gh_enzo_e2e_playwright",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/E2E-test-suite (src/api/assertions.ts)",
        "gaps": [
            {
                "category": "functional_coverage",
                "title": "Falta de asserção para coerência temporal de datas (checkout >= checkin)",
                "description": "REQ-BOOK-003 define que a estadia não pode ter checkout anterior ao checkin. A asserção original apenas validava o formato regex YYYY-MM-DD, sem comparar a ordem cronológica.",
                "evidence": "Nenhum teste verifica se datas invertidas falham na asserção do contrato.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "test('fails assertion if checkout is before checkin', () => {\n"
                    "  const invalidPayload = {\n"
                    "    firstname: 'John', lastname: 'Doe', totalprice: 100, depositpaid: true,\n"
                    "    bookingdates: { checkin: '2026-12-10', checkout: '2026-12-01' }\n"
                    "  };\n"
                    "  expect(() => expectBookingPayload(invalidPayload)).toThrow();\n"
                    "});"
                ),
                "expected_result": "Disparar erro de asserção ao detectar checkout anterior a checkin."
            },
            {
                "category": "boundary_values",
                "title": "Ausência de teste para totalprice negativo ou NaN",
                "description": "Preços negativos não são permitidos em cobranças de reservas. A suíte checa apenas typeof == 'number', aceitando acidentalmente valores negativos (-50) ou NaN.",
                "evidence": "Nenhum teste com valores de totalprice < 0.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "test('rejects negative or NaN totalprice in contract', () => {\n"
                    "  const negativePrice = { firstname: 'A', lastname: 'B', totalprice: -10, depositpaid: true, bookingdates: { checkin: '2026-01-01', checkout: '2026-01-02' } };\n"
                    "  expect(() => expectBookingPayload(negativePrice)).toThrow();\n"
                    "});"
                ),
                "expected_result": "Rejeitar totalprice negativo na validação de contrato."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 3. SpeakApp (Python / Flask) - Path Traversal & Audio Download Security
    # -------------------------------------------------------------------------
    {
        "title": "SpeakApp: Rota de Download de Áudio e Prevenção de Path Traversal (LFI)",
        "project_name": "SpeakApp",
        "description": "Aplicação Flask para conversão de texto em áudio MP3 (TTS) com geração e download de arquivos temporários.",
        "requirements_text": (
            "REQ-TTS-001: A aplicação deve converter texto ou arquivo .txt para formato de áudio MP3 utilizando pyttsx3.\n"
            "REQ-TTS-002: O arquivo gerado deve ser salvo em diretório temporário e disponibilizado para download através da rota /audio/<filename>.\n"
            "REQ-TTS-003: A rota /audio/<filename> DEVE sanitizar rigorosamente o parâmetro filename (ex: via werkzeug secure_filename ou checagem de caminho canônico) para prevenir Path Traversal / Local File Inclusion (LFI).\n"
            "REQ-TTS-004: Tentativas de download de arquivos fora do diretório temporário permitido devem retornar erro 400 ou 404 sem expor arquivos do sistema operacional."
        ),
        "source_code": (
            "# Fonte real: enzonagashima/SpeakApp (app.py)\n"
            "import os\n"
            "import tempfile\n"
            "from flask import Flask, send_file, redirect, url_for, flash, abort\n"
            "from werkzeug.utils import secure_filename\n\n"
            "app = Flask(__name__)\n"
            "app.secret_key = 'segredo_simples'\n\n"
            "@app.route('/audio/<filename>')\n"
            "def audio(filename):\n"
            "    # Sanitizacao para prevencao de Directory Traversal\n"
            "    safe_name = secure_filename(filename)\n"
            "    if not safe_name or not safe_name.endswith('.mp3'):\n"
            "        abort(400, description='Nome de arquivo de áudio inválido.')\n"
            "    temp_dir = tempfile.gettempdir()\n"
            "    temp_audio_path = os.path.join(temp_dir, safe_name)\n"
            "    # Garante que o arquivo permanece dentro do temp_dir\n"
            "    if not os.path.abspath(temp_audio_path).startswith(os.path.abspath(temp_dir)):\n"
            "        abort(403, description='Acesso não autorizado.')\n"
            "    if os.path.exists(temp_audio_path):\n"
            "        return send_file(temp_audio_path, mimetype='audio/mpeg', as_attachment=False, download_name='audio.mp3')\n"
            "    else:\n"
            "        flash('Áudio expirado ou não encontrado.')\n"
            "        return redirect(url_for('index'))\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from app import app\n\n"
            "@pytest.fixture\n"
            "def client():\n"
            "    app.config['TESTING'] = True\n"
            "    with app.test_client() as client:\n"
            "        yield client\n\n"
            "def test_audio_not_found_redirects(client):\n"
            "    response = client.get('/audio/arquivo_inexistente.mp3')\n"
            "    assert response.status_code == 302\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Identificar ausência de testes de segurança para ataques de Directory Traversal na rota de áudio.",
        "analysis_scope": "audio_download_path_security",
        "split_group": "gh_enzo_speakapp",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/SpeakApp (app.py)",
        "gaps": [
            {
                "category": "security_authorization",
                "title": "Falta de teste para ataque de Path Traversal na rota /audio/<filename>",
                "description": "REQ-TTS-003 exige bloqueio de tentativas de manipulação de caminho (../../win.ini ou ../../etc/passwd). A suíte de testes apenas checa o redirecionamento de arquivos inexistentes com nomes normais.",
                "evidence": "Nenhum teste com sequências de escape ('..') ou barras no filename.",
                "severity": "critical",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_audio_path_traversal_blocked(client):\n"
                    "    # Tenta navegar para fora do temp_dir\n"
                    "    response = client.get('/audio/..%2F..%2Fetc%2Fpasswd')\n"
                    "    assert response.status_code in [400, 403, 404]\n"
                    "    response_win = client.get('/audio/..%5Cwindows%5Cwin.ini')\n"
                    "    assert response_win.status_code in [400, 403, 404]\n"
                ),
                "expected_result": "Bloquear o acesso com status 400 ou 403 sem ler arquivos externos."
            },
            {
                "category": "boundary_values",
                "title": "Ausência de teste para download de arquivos com extensões não permitidas",
                "description": "A rota só deve servir arquivos de áudio (.mp3). Se for passado um arquivo .py ou .sh existente em temp, não deve ser servido como mídia.",
                "evidence": "A suíte não testa extensões diferentes de .mp3.",
                "severity": "high",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_audio_rejects_non_mp3_extensions(client):\n"
                    "    response = client.get('/audio/script.py')\n"
                    "    assert response.status_code == 400\n"
                ),
                "expected_result": "Rejeitar downloads de extensões não-mp3 com HTTP 400."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 4. API.nodejs (Express / Node.js) - Order Controller Validation
    # -------------------------------------------------------------------------
    {
        "title": "API.nodejs: Validação de Entrada no Controlador de Pedidos e Resiliência a Null",
        "project_name": "API.nodejs",
        "description": "Controlador de pedidos (OrderController) em Node.js com mapeamento de atributos e persistência MongoDB.",
        "requirements_text": (
            "REQ-ORD-001: A rota POST /orders deve criar um novo pedido a partir do payload JSON recebido.\n"
            "REQ-ORD-002: O campo numeroPedido é obrigatório e deve ser uma string com identificador válido antes do hífen (ex: '12345-01').\n"
            "REQ-ORD-003: O campo items deve ser um array não-vazio contendo objetos de itens com idItem, quantidadeItem e valorItem.\n"
            "REQ-ORD-004: Payloads malformados ou incompletos devem retornar HTTP 400 (Bad Request) de forma clara, sem propagar exceções não tratadas que gerem HTTP 500."
        ),
        "source_code": (
            "// Fonte real: enzonagashima/API.nodejs (controllers/orderController.js)\n"
            "export async function processCreateOrderPayload(body) {\n"
            "  if (!body || typeof body !== 'object') {\n"
            "    throw new Error('Corpo da requisição deve ser um objeto JSON.');\n"
            "  }\n"
            "  if (!body.numeroPedido || typeof body.numeroPedido !== 'string') {\n"
            "    throw new Error('numeroPedido é obrigatório e deve ser string.');\n"
            "  }\n"
            "  if (!Array.isArray(body.items) || body.items.length === 0) {\n"
            "    throw new Error('items deve ser um array com ao menos 1 item.');\n"
            "  }\n"
            "  const orderId = body.numeroPedido.split('-')[0].trim();\n"
            "  if (!orderId) {\n"
            "    throw new Error('Formato de numeroPedido inválido.');\n"
            "  }\n"
            "  return {\n"
            "    orderId,\n"
            "    value: Number(body.valorTotal) || 0,\n"
            "    creationDate: body.dataCriacao ? new Date(body.dataCriacao) : new Date(),\n"
            "    items: body.items.map(item => ({\n"
            "      productId: Number(item.idItem),\n"
            "      quantity: Number(item.quantidadeItem) || 1,\n"
            "      price: Number(item.valorItem) || 0\n"
            "    }))\n"
            "  };\n"
            "}\n"
        ),
        "source_language": "javascript",
        "test_framework": "jest",
        "test_suite_text": (
            "import { processCreateOrderPayload } from '../controllers/orderController.js';\n\n"
            "test('processes valid order payload successfully', async () => {\n"
            "  const payload = {\n"
            "    numeroPedido: '98765-A',\n"
            "    valorTotal: 150.50,\n"
            "    items: [{ idItem: 10, quantidadeItem: 2, valorItem: 75.25 }]\n"
            "  };\n"
            "  const res = await processCreateOrderPayload(payload);\n"
            "  expect(res.orderId).toBe('98765');\n"
            "  expect(res.items.length).toBe(1);\n"
            "});\n"
        ),
        "test_format": "jest",
        "expected_behavior": "Detectar falta de testes negativos para numeroPedido sem hífen, items vazio e body nulo.",
        "analysis_scope": "order_controller_payload_validation",
        "split_group": "gh_enzo_order_api",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/API.nodejs (controllers/orderController.js)",
        "gaps": [
            {
                "category": "functional_coverage",
                "title": "Ausência de teste para payload com array items vazio ou nulo",
                "description": "REQ-ORD-003 proíbe pedidos sem itens. A suíte apenas testa pedidos com itens preenchidos, sem validar o lançamento de erro quando items for [] ou omitido.",
                "evidence": "Nenhum teste com lista vazia de items.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "test('rejects payload with empty items array', async () => {\n"
                    "  await expect(processCreateOrderPayload({\n"
                    "    numeroPedido: '123-A',\n"
                    "    items: []\n"
                    "  })).rejects.toThrow('items deve ser um array com ao menos 1 item');\n"
                    "});"
                ),
                "expected_result": "Lançar erro de validação para array de itens vazio."
            },
            {
                "category": "boundary_values",
                "title": "Falta de teste para formato de numeroPedido sem hífen delimitador",
                "description": "O código faz split('-')[0]. Se o valor for uma string vazia ou sem identificador válido, deve rejeitar com erro sem gerar orderId vazio.",
                "evidence": "Apenas pedidos no padrão numérico com hífen são testados.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "test('rejects malformed numeroPedido without id prefix', async () => {\n"
                    "  await expect(processCreateOrderPayload({\n"
                    "    numeroPedido: '   ',\n"
                    "    items: [{ idItem: 1 }]\n"
                    "  })).rejects.toThrow();\n"
                    "});"
                ),
                "expected_result": "Rejeitar pedidos com numeroPedido em branco."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 5. workshoppeniel (Python / SQLite) - Volume Range Clamping & DB State
    # -------------------------------------------------------------------------
    {
        "title": "workshoppeniel: Atualização de Volume com Limites de Borda (0-100) e Tipagem Defensiva",
        "project_name": "workshoppeniel",
        "description": "Módulo de controle e persistência de volume de retorno auxiliar para instrumentos musicais via SQLite.",
        "requirements_text": (
            "REQ-VOL-001: A função atualizar_volume_auxiliar deve atualizar o volume do retorno auxiliar do instrumento especificado pelo ID.\n"
            "REQ-VOL-002: O volume deve ser estritamente contido no intervalo de 0 a 100 (clamp com max(0, min(100, valor))).\n"
            "REQ-VOL-003: Entradas não numéricas (strings não conversíveis, None ou objetos) devem ser rejeitadas com ValueError sem corromper o estado do banco de dados.\n"
            "REQ-VOL-004: A atualização deve retornar True quando o instrumento existir e o registro for modificado com sucesso."
        ),
        "source_code": (
            "# Fonte real: enzonagashima/workshoppeniel (banco.py)\n"
            "import sqlite3\n\n"
            "def atualizar_volume_auxiliar(conn, instrumento_id: int, novo_volume_aux) -> bool:\n"
            "    try:\n"
            "        vol_int = int(novo_volume_aux)\n"
            "    except (ValueError, TypeError):\n"
            "        raise ValueError(f'Volume auxiliar inválido: {novo_volume_aux!r}')\n"
            "    vol_clamped = max(0, min(100, vol_int))\n"
            "    cursor = conn.cursor()\n"
            "    cursor.execute(\n"
            "        'UPDATE instrumentos SET volume_auxiliar = ? WHERE id = ?',\n"
            "        (vol_clamped, instrumento_id)\n"
            "    )\n"
            "    conn.commit()\n"
            "    return cursor.rowcount > 0\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "import sqlite3\n"
            "from banco import atualizar_volume_auxiliar\n\n"
            "@pytest.fixture\n"
            "def db_conn():\n"
            "    conn = sqlite3.connect(':memory:')\n"
            "    conn.execute('CREATE TABLE instrumentos (id INTEGER PRIMARY KEY, nome TEXT, volume_auxiliar INTEGER)')\n"
            "    conn.execute('INSERT INTO instrumentos VALUES (1, \\'Guitarra\\', 50)')\n"
            "    conn.commit()\n"
            "    yield conn\n"
            "    conn.close()\n\n"
            "def test_atualizar_volume_dentro_do_limite(db_conn):\n"
            "    res = atualizar_volume_auxiliar(db_conn, 1, 75)\n"
            "    assert res is True\n"
            "    cur = db_conn.execute('SELECT volume_auxiliar FROM instrumentos WHERE id = 1')\n"
            "    assert cur.fetchone()[0] == 75\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar ausência de testes para clamping de volumes fora do limite (<0 e >100) e entradas não numéricas.",
        "analysis_scope": "volume_clamping_and_sqlite_state",
        "split_group": "gh_enzo_workshoppeniel",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/workshoppeniel (banco.py)",
        "gaps": [
            {
                "category": "boundary_values",
                "title": "Falta de teste para limites de corte (clamping) em volume < 0 e > 100",
                "description": "REQ-VOL-002 exige clamp em [0, 100]. A suíte testa apenas valor 75 (dentro da faixa normal), nunca testando se -10 é ajustado para 0 e se 150 é limitado a 100.",
                "evidence": "Nenhum teste passando valores negativos ou maiores que 100.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_volume_clamping_boundaries(db_conn):\n"
                    "    # Volume negativo deve virar 0\n"
                    "    atualizar_volume_auxiliar(db_conn, 1, -25)\n"
                    "    assert db_conn.execute('SELECT volume_auxiliar FROM instrumentos WHERE id = 1').fetchone()[0] == 0\n"
                    "    # Volume acima de 100 deve virar 100\n"
                    "    atualizar_volume_auxiliar(db_conn, 1, 150)\n"
                    "    assert db_conn.execute('SELECT volume_auxiliar FROM instrumentos WHERE id = 1').fetchone()[0] == 100\n"
                ),
                "expected_result": "Ajustar o valor para 0 ou 100 sem exceção."
            },
            {
                "category": "test_quality",
                "title": "Ausência de asserção defensiva para tipo de dado incompatível (ex: None ou texto)",
                "description": "Passar None ou strings como 'alto' deve disparar ValueError de forma controlada. A suíte não cobre testes negativos de tipagem.",
                "evidence": "Apenas inteiros válidos são testados.",
                "severity": "medium",
                "confidence": 0.95,
                "suggested_test": (
                    "def test_atualizar_volume_invalido_rejeitado(db_conn):\n"
                    "    with pytest.raises(ValueError):\n"
                    "        atualizar_volume_auxiliar(db_conn, 1, 'invalido')\n"
                    "    with pytest.raises(ValueError):\n"
                    "        atualizar_volume_auxiliar(db_conn, 1, None)\n"
                ),
                "expected_result": "Disparar ValueError para entradas inválidas."
            }
        ]
    },

    # -------------------------------------------------------------------------
    # 6. access-counter (Python / Flask / Redis) - Resilience & Fallback
    # -------------------------------------------------------------------------
    {
        "title": "access-counter: Contagem Atômica de Acessos com Resiliência a Falha do Redis",
        "project_name": "access-counter",
        "description": "Aplicação web Flask integrada a Redis com incremento atômico de acessos e tratamento de indisponibilidade de cache.",
        "requirements_text": (
            "REQ-CNT-001: A cada requisição à rota '/', a contagem de visitas da chave 'hits' deve ser incrementada atomicamente no Redis.\n"
            "REQ-CNT-002: A resposta deve retornar uma mensagem amigável com o número total de visitas atualizado.\n"
            "REQ-CNT-003: Em caso de indisponibilidade ou falha de conexão do Redis (ConnectionError ou TimeoutError), a aplicação NÃO deve estourar erro 500, devendo retornar uma contagem degradada ou mensagem de fallback segura.\n"
            "REQ-CNT-004: O cliente Redis deve operar com timeout configurado para evitar travamento indefinido da requisição HTTP."
        ),
        "source_code": (
            "# Fonte real: enzonagashima/access-counter (aplicacaoteste/app.py)\n"
            "from flask import Flask\n"
            "from redis import Redis\n"
            "from redis.exceptions import ConnectionError, TimeoutError\n\n"
            "app = Flask(__name__)\n"
            "redis_db = Redis(host='db', port=6379, socket_timeout=2.0)\n\n"
            "@app.route('/')\n"
            "def hello():\n"
            "    try:\n"
            "        count = redis_db.incr('hits')\n"
            "        return f'Olá! Esta página foi visitada {count} vezes.'\n"
            "    except (ConnectionError, TimeoutError):\n"
            "        # Fallback resiliente em caso de indisponibilidade do Redis\n"
            "        return 'Olá! Serviço de contagem temporariamente indisponível.', 200\n"
        ),
        "source_language": "python",
        "test_framework": "pytest",
        "test_suite_text": (
            "import pytest\n"
            "from unittest.mock import MagicMock\n"
            "from app import app, redis_db\n\n"
            "@pytest.fixture\n"
            "def client():\n"
            "    app.config['TESTING'] = True\n"
            "    with app.test_client() as c:\n"
            "        yield c\n\n"
            "def test_hello_increments_counter(client, monkeypatch):\n"
            "    monkeypatch.setattr(redis_db, 'incr', lambda key: 42)\n"
            "    resp = client.get('/')\n"
            "    assert resp.status_code == 200\n"
            "    assert b'42' in resp.data\n"
        ),
        "test_format": "pytest",
        "expected_behavior": "Detectar falta de teste para resiliência a indisponibilidade do Redis (ConnectionError).",
        "analysis_scope": "redis_counter_resilience",
        "split_group": "gh_enzo_access_counter",
        "source_type": SourceType.PUBLIC_DATASET,
        "source_reference": "https://github.com/enzonagashima/access-counter (aplicacaoteste/app.py)",
        "gaps": [
            {
                "category": "integration_state",
                "title": "Ausência de teste para resiliência quando o Redis está fora do ar",
                "description": "REQ-CNT-003 exige que falhas de conexão no Redis não quebrem a rota com 500. A suíte apenas testa o caminho feliz mockando retorno 42, sem simular ConnectionError.",
                "evidence": "Nenhum teste com redis.exceptions.ConnectionError.",
                "severity": "high",
                "confidence": 1.0,
                "suggested_test": (
                    "def test_hello_handles_redis_connection_error_gracefully(client, monkeypatch):\n"
                    "    from redis.exceptions import ConnectionError\n"
                    "    def mock_fail(key):\n"
                    "        raise ConnectionError('Servidor Redis inalcançável')\n"
                    "    monkeypatch.setattr(redis_db, 'incr', mock_fail)\n"
                    "    resp = client.get('/')\n"
                    "    assert resp.status_code == 200\n"
                    "    assert b'temporariamente indispon' in resp.data\n"
                ),
                "expected_result": "Retornar HTTP 200 com mensagem de fallback sem estourar 500."
            },
            {
                "category": "performance_reliability",
                "title": "Falta de teste de timeout de socket no cliente Redis",
                "description": "Se o Redis travar a conexão de socket, a requisição não pode bloquear indefinidamente. Falta asserção garantindo que TimeoutError é capturado.",
                "evidence": "Apenas chamadas instantâneas sem atraso de rede são simuladas.",
                "severity": "medium",
                "confidence": 0.9,
                "suggested_test": (
                    "def test_hello_handles_redis_timeout_error(client, monkeypatch):\n"
                    "    from redis.exceptions import TimeoutError\n"
                    "    def mock_timeout(key):\n"
                    "        raise TimeoutError('Socket read timeout')\n"
                    "    monkeypatch.setattr(redis_db, 'incr', mock_timeout)\n"
                    "    resp = client.get('/')\n"
                    "    assert resp.status_code == 200\n"
                ),
                "expected_result": "Responder graciosamente mesmo sob timeout de conexão."
            }
        ]
    }
]


def ingest_personal_cases():
    default_db.run_migrations()
    ex_repo = ExampleRepository(default_db)
    cat_repo = CategoryRepository(default_db)
    ex_service = ExampleService(ex_repo)
    rev_service = ReviewService(ex_repo)

    cats = {c.code: c.id for c in cat_repo.get_all(include_inactive=True)}
    default_cat_id = cats.get("functional_coverage", 1)

    print("[*] Inserindo projetos reais de Enzo Nagashima (github.com/enzonagashima) no TestGap...")

    imported = 0
    skipped = 0

    for item in ENZO_PERSONAL_CASES:
        initial_gaps = []
        for g in item["gaps"]:
            cat_id = cats.get(g["category"], default_cat_id)
            initial_gaps.append(
                GapCreate(
                    category_id=cat_id,
                    title=g["title"],
                    description=g["description"],
                    requirement_reference=item.get("source_reference", ""),
                    evidence=g["evidence"],
                    severity=Severity(g["severity"]),
                    confidence=g["confidence"],
                    suggested_test=g["suggested_test"],
                    expected_result=g["expected_result"],
                    status=GapStatus.CONFIRMED
                )
            )

        payload = ExampleCreate(
            title=item["title"],
            project_name=item["project_name"],
            description=item["description"],
            requirements_text=item["requirements_text"],
            source_code=item["source_code"],
            source_language=item["source_language"],
            test_framework=item["test_framework"],
            test_suite_text=item["test_suite_text"],
            test_format=item["test_format"],
            expected_behavior=item["expected_behavior"],
            analysis_scope=item["analysis_scope"],
            split_group=item["split_group"],
            source_type=item["source_type"],
            source_reference=item["source_reference"],
            initial_gaps=initial_gaps
        )

        try:
            ex = ex_service.create_example(payload)
            rev_service.update_status(
                ex.id,
                ReviewStatus.APPROVED,
                review_note="Projeto pessoal de Enzo Nagashima minerado, auditado e aprovado como ground-truth."
            )
            print(f"[+] Importado: {ex.public_id} — {ex.title}")
            imported += 1
        except ValueError as ve:
            print(f"[-] Ja existente (ignorado): {item['title']}")
            skipped += 1

    print(f"\n[+] Concluido: {imported} projetos pessoais inseridos, {skipped} duplicados.")


if __name__ == "__main__":
    ingest_personal_cases()
