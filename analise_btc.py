import time
import schedule
import pandas as pd
from binance.client import Client
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from datetime import datetime

# Configurar a API da Binance
API_KEY = ''
API_SECRET = ''

# Configurar o cliente da Binance
def configure_binance_client():
    global client
    client = Client(API_KEY, API_SECRET, requests_params={"timeout": 20})
    try:
        sync_time()
        print("|| Status da Conexão: Sucesso                                            ||")
    except Exception as e:
        print(f"|| Status da Conexão: Falha ({e})                                       ||")

        exit()

# Função para sincronizar o horário
def sync_time():
    try:
        server_time = client.get_server_time()['serverTime']
        local_time = int(time.time() * 1000)
        client.TIME_OFFSET = server_time - local_time
    except Exception as e:
        print(f"Erro ao sincronizar horário: {e}")
        exit()

# Função para obter dados históricos do BTC/USDT
def get_historical_data(symbol='BTCUSDT', interval='30m', limit=100):
    sync_time()
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data['close'] = data['close'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)
    data['volume'] = data['volume'].astype(float)
    return data[['time', 'close', 'high', 'low', 'volume']]

# Função para obter o preço atual em tempo real
def get_current_price(symbol='BTCUSDT'):
    sync_time()
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

# Função para analisar o mercado
def analyze_market(data):
    # Indicadores técnicos
    data['ema'] = EMAIndicator(close=data['close'], window=14).ema_indicator()
    data['rsi'] = RSIIndicator(close=data['close'], window=14).rsi()
    data['macd'] = MACD(close=data['close']).macd()
    data['macd_signal'] = MACD(close=data['close']).macd_signal()
    data['atr'] = AverageTrueRange(high=data['high'], low=data['low'], close=data['close']).average_true_range()
    bb = BollingerBands(close=data['close'], window=20, window_dev=2)
    data['bb_high'] = bb.bollinger_hband()
    data['bb_low'] = bb.bollinger_lband()

    # Estratégia avançada
    last_close = data['close'].iloc[-1]
    last_ema = data['ema'].iloc[-1]
    last_rsi = data['rsi'].iloc[-1]
    macd = data['macd'].iloc[-1]
    macd_signal = data['macd_signal'].iloc[-1]
    bb_high = data['bb_high'].iloc[-1]
    bb_low = data['bb_low'].iloc[-1]
    atr = data['atr'].iloc[-1]

    strategy = ""
    if last_close < bb_low and last_rsi < 30 and macd < macd_signal:
        strategy = f"Compra: Preço abaixo da banda inferior, RSI sobrevendido, e MACD indicando baixa. ATR: {atr:.2f}"
    elif last_close > bb_high and last_rsi > 70 and macd > macd_signal:
        strategy = f"Venda: Preço acima da banda superior, RSI sobrecomprado, e MACD indicando alta. ATR: {atr:.2f}"
    else:
        strategy = "Aguardar: Sem sinais claros de compra/venda."

    return strategy

# Inicializar o script
print("===========================================================================")
print("||                   Analise de mercado - BTC/USDT                       ||")
print("||                   Desenvolvido por Lucas Santos                       ||")
print("|| Não use em conta real, robo desenvolvido para estudos                 ||")
print("||=======================================================================||")
print("|| Conexão com a API: Conectando...                                      ||")

configure_binance_client()

print("|| Realizando análise inicial...                                         ||")
valor_atual = get_current_price()
print(f"|| Valor atual do BTC/USDT: {valor_atual:.2f}                                     ||")
print("===========================================================================")
print("|| ATENÇÃO: Este robô foi desenvolvido apenas para fins de estudo.       ||")
print("|| Não confie nos sinais gerados para tomar decisões financeiras reais.  ||")
print("|| O uso deste robô é por sua conta e risco.                             ||")
print("|| Desenvolvedor não se responsabiliza por quaisquer perdas financeiras. ||")
print("|| Use apenas em ambientes simulados e com fins educacionais.            ||")
print("==========================================================================")

# Realizar análise inicial
data = get_historical_data()
initial_strategy = analyze_market(data)
print(f"\nAnalise Resultado: {initial_strategy}\n")

# Função principal para executar periodicamente
def run_strategy():
    print(f"\n[{datetime.now()}] Analisando mercado...\n")
    data = get_historical_data()
    strategy = analyze_market(data)
    print(f"Analise Resultado: {strategy}")

# Agendar a execução a cada 30 minutos
schedule.every(30).minutes.do(run_strategy)

print("Iniciando script de análise BTC/USDT...\n")

while True:
    schedule.run_pending()
    time.sleep(1)
