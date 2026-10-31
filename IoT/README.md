# Handoff para Raphael - MicroPython / Wokwi

O backend está preparado para sua parte. Você continua responsável por `main.py`, sensores, diagrama/pinagem Wokwi, Wi-Fi, feedback visual e link público. `transport.py` é um helper opcional e **não representa a simulação concluída**.

## Contrato estável v1

`POST {API_URL}/api/v1/readings`, `Content-Type: application/json`, header `X-Device-Key: <chave de demonstração>`. Veja `telemetry.example.json` e a documentação interativa `{API_URL}/docs`.

- `event_id`: texto único por leitura (1-100 caracteres: letras, números, `_` e `-`). Inclua um identificador novo por boot + contador. **Reenvio deve manter o mesmo ID e payload.**
- `device_id`: `esp32-001`; `patient_id`: `demo-001`. A chave só aceita essa associação. Ajustes devem ser combinados com o backend.
- `temperature_c`: número entre 10 e 50; `heart_rate_bpm`: inteiro entre 30 e 240.
- `movement_detected`, `emergency_button_pressed`: booleanos JSON reais (`true`/`false`).
- `schema_version`: `"1.0"` (padrão).
- Opcionais: `spo2_percent` (50-100), `systolic_bp` (50-250).
- `timestamp` é opcional. Omitir evita problemas com relógio da placa; o servidor marca a hora UTC. Se enviar, use ISO 8601 com `Z`/offset e sincronize o relógio; janela de 24 h atrás até 5 min à frente.

Resposta HTTP 200 (recorte):

```json
{"event_id":"esp32-boot001-000001","duplicate":false,"feedback":{"led":"green","label":"NORMAL"}}
```

| Situação simulada | `feedback.led` | `feedback.label` |
|---|---|---|
| 36,6 °C, 76 bpm, movimento, sem botão | green | NORMAL |
| Sem movimento | yellow | MEDIUM |
| Temperatura >38 °C ou FC >120 bpm | red | HIGH |
| Botão de emergência | red | CRITICAL |

O retorno inclui também `prediction`, `sensor_alerts`, `received_at` e `feature_provenance`. **LED representa as regras de sensor da fase 3.** O risco ML da fase 6 é operacional/hospitalar e usa entradas sintéticas adicionais; não é diagnóstico individual.

## Implementação recomendada

1. Usar ESP32 com MicroPython no Wokwi (a FIAP também aceita ESP32; não exige Raspberry Pi especificamente). Wi-Fi `Wokwi-GUEST`, senha vazia.
2. Capturar temperatura e batimento simulado; selecionar pinos e componentes a seu critério.
3. Enviar uma amostra a cada 5 segundos. A interface marca dados antigos após 30 segundos sem amostra recente.
4. Usar `feedback.led`/`label` no LED RGB ou OLED. Não recalcular risco de ML na placa.
5. Em timeout, guardar e repetir a mesma amostra; backoff 5, 10, 20, 30 s. Sempre fechar a resposta HTTP (`transport.py` já faz isso). Ao recuperar conexão, voltar ao intervalo normal.
6. HTTP 401: conferir chave. 403: conferir IDs. 409: ID reutilizado com conteúdo alterado. 422: payload inválido. 429: aguardar `Retry-After`. 5xx: retry com backoff; manter indicação de falha de conexão.
7. A chave fica em `config.py` local (ignorado pelo Git) ou entrada na console durante a simulação. Não incluir a chave reutilizável em projeto Wokwi público; combinar entrada manual para apresentação.

O Wokwi público precisa de URL HTTPS pública do backend. `localhost` não aponta para o computador do grupo. O gateway privado é uma alternativa de desenvolvimento, não necessária na entrega publicada.

## Já é possível testar sem hardware

Na raiz da fase 7, com backend local executando:

```bash
.venv/bin/python scripts/simulate_sensor.py
.venv/bin/python scripts/simulate_sensor.py --alert
```

O script usa a chave do `.env` local. Para produção, usar `--url https://<backend-publicado>` e a chave correspondente ao ambiente. A URL definitiva e a chave serão entregues separadamente após o deploy; não há URL fictícia funcionando neste documento.

## Aceite conjunto

- Mostrar no vídeo a leitura do Wokwi, HTTP 200 e mudança no LED/OLED.
- Em até um ciclo de consulta (5 s + rede), confirmar o mesmo `event_id`/valores no Web/APK.
- Testar cenário normal, alerta e botão; desconectar o sensor e comprovar estado sem sinal recente.
- Registrar link público do Wokwi em `docs/DELIVERY.md` e no README.

Referências: [MicroPython](https://docs.wokwi.com/guides/micropython), [rede ESP32](https://docs.wokwi.com/guides/esp32-wifi).
