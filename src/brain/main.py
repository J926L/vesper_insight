from collections import deque
from rich.console import Console
from rich.table import Table
from rich.live import Live
from icecream import ic

from model import setup_cuda_limits, AnomalyDetector
from processor import FlowConsumer, FeatureExtractor
from storage import AlertStorage

console = Console()

def run_brain():
    # 1. Setup CUDA
    setup_cuda_limits()

    # 2. Initialize Components
    detector = AnomalyDetector()
    consumer = FlowConsumer(bootstrap_servers="localhost:19092", topic="raw_metrics")
    storage = AlertStorage()
    extractor = FeatureExtractor()

    # 配置 icecream
    ic.configureOutput(prefix="ic| ")
    ic("AI Engine Started. Monitoring flows...")

    # 使用 deque 存储最近的 10 条记录，确保渲染稳定性
    history = deque(maxlen=10)

    def generate_table() -> Table:
        table = Table(title="Vesper Insight - Real-time Analysis", expand=True)
        table.add_column("Timestamp", style="cyan", no_wrap=True)
        table.add_column("Flow", style="magenta")
        table.add_column("Score", style="green")
        table.add_column("Status", style="bold red")
        
        for row in history:
            table.add_row(*row)
        return table

    # 计算处理数量，提示模型预热状态
    count = 0
    warmup_limit = 50

    # 3. Execution Loop
    with Live(generate_table(), console=console, refresh_per_second=4) as live:
        try:
            while True:
                flow = consumer.poll(timeout=1.0)
                if flow:
                    count += 1
                    features = extractor.extract(flow)
                    
                    # Compute score and learn
                    score = detector.score_one(features)
                    detector.learn_one(features)
                    
                    status = "[dim white]NORMAL[/]"
                    if count < warmup_limit:
                        status = "[yellow]WARMING[/]"
                    elif score > 0.8:  # 异常阈值
                        status = "[bold red]ALERT[/]"
                        storage.save_alert(flow, score)
                        live.console.log(f"[bold red]!!! ANOMALY !!! {flow.get('src_ip')} -> {flow.get('dst_ip')} Score: {score:.4f}")
                    
                    # 更新历史记录并刷新表格
                    history.append((
                        str(flow.get("timestamp")),
                        f"{flow.get('src_ip')} -> {flow.get('dst_ip')}",
                        f"{score:.4f}",
                        status
                    ))
                    # 实时调试输出特征熵
                    if count % 10 == 0:
                        ic(f"Sample #{count} Features: {features} | Score: {score}")
                    
                    live.update(generate_table())
                
        except KeyboardInterrupt:
            ic("Stopping...")
        finally:
            consumer.close()

if __name__ == "__main__":
    run_brain()
