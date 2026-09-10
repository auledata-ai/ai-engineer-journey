src/clients.py tem tres funcoes com a mesma logica de retry copiada e colada.
Extraia essa logica para um decorator `retry(times: int, exceptions: tuple)` no mesmo arquivo
e aplique-o nas tres funcoes, sem mudar o comportamento. Os testes existentes devem continuar
passando e ha um teste novo que verifica o decorator. Rode `pytest -q`. Nao altere os testes.
