import os
import json
from pathlib import Path
import config

MAX_BYTES_PER_FILE = config.MAX_BYTES_PER_FILE


def write_jsonl_safely(chunks, output_dir, base_name="drift_output"):
    """
    Ghi dữ liệu ra nhiều file JSONL, mỗi file ≤ MAX_BYTES_PER_FILE.
    Nếu chunk > MAX_BYTES_PER_FILE thì chia nhỏ ra nhiều file riêng (tăng idx mỗi phần).

    Args:
        chunks: List[dict] - danh sách các chunk đã chuẩn hóa.
        output_dir: str hoặc Path - thư mục đầu ra.
        base_name: str - tên cơ sở cho file JSONL.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    idx = 0
    buffer = []
    buffer_size = 0

    def flush_buffer():
        nonlocal idx, buffer, buffer_size
        if not buffer:
            return
        output_file = output_dir / f"{base_name}_{idx}.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(buffer)
        print(
            f"✅ Saved {output_file} ({len(buffer)} chunks, {buffer_size/1024:.1f} KB)"
        )
        idx += 1
        buffer.clear()
        buffer_size = 0

    for chunk in chunks:
        json_line = json.dumps(chunk, ensure_ascii=False) + "\n"
        json_bytes = json_line.encode("utf-8")
        json_size = len(json_bytes)

        # 🔹 Nếu chunk vượt quá giới hạn file → chia nhỏ ra nhiều file riêng
        if json_size > MAX_BYTES_PER_FILE:
            flush_buffer()
            print(f"⚠️ Large chunk detected ({json_size/1024:.1f} KB), splitting...")

            parts = [
                json_bytes[i : i + MAX_BYTES_PER_FILE]
                for i in range(0, len(json_bytes), MAX_BYTES_PER_FILE)
            ]

            for part_bytes in parts:
                part_str = part_bytes.decode("utf-8", errors="ignore")
                output_file = output_dir / f"{base_name}_{idx}.jsonl"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(part_str + "\n")
                print(
                    f"🪓 Split chunk saved: {base_name}_{idx}.jsonl ({len(part_bytes)/1024:.1f} KB)"
                )
                idx += 1
            continue

        # Nếu cộng thêm chunk mới mà vượt giới hạn → ghi file mới
        if buffer_size + json_size > MAX_BYTES_PER_FILE:
            flush_buffer()

        buffer.append(json_line)
        buffer_size += json_size

    flush_buffer()
