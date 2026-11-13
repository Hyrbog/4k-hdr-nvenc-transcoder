# 4K HDR Batch Video Transcoder (NVIDIA NVENC)

A modular, CLI-driven Python batch transcoding engine designed for high-throughput video processing. Built to automate large-scale media queues using **FFmpeg**, **FFprobe**, and **MKVToolNix**, featuring **NVIDIA NVENC (HEVC/x265)** hardware acceleration, **HDR-to-SDR (BT.709) tonemapping**, and a real-time ANSI terminal dashboard.

## Key Features
- **Modular Architecture:** Clean separation of concerns across 9 dedicated Python modules handling configuration, stream probing, queue scanning, ETA calculation, transcoding execution, and terminal UI rendering.
- **Hardware-Accelerated Encoding (CUDA / NVENC):** Offloads heavy HEVC/x265 encoding to NVIDIA GPUs (`hevc_nvenc`) while executing hybrid CPU/GPU color-space pipelines (`zscale` + Hable tonemapping) to prevent VRAM bottlenecks and driver hangs.
- **Deep Stream Inspection (`FFprobe`):** Automatically inspects video streams to detect true codecs (`x264`/`x265`), HDR color primaries (`BT.2020`, `SMPTE2084`, `HLG`), audio tracks, and forced subtitle flags before processing.
- **Lossless Container Remuxing:** Detects `.mp4` inputs and transparently remuxes them into `.mkv` containers via `mkvmerge` prior to encoding to preserve track integrity.
- **Real-Time ANSI Progress Dashboard:** Custom terminal UI using ANSI escape sequences (`\033[K`, `\033[3A`) to render live progress bars, FPS, encoding speed multipliers, and dynamic multi-tier ETAs (current video, current folder, and global queue).
- **Fault Tolerance & Atomic File Operations:** Writes to temporary staging files before moving completed outputs, isolates corrupted headers (`duration <= 0`), and logs failed jobs with FFmpeg exit codes to a dedicated audit log (`videos_corruptos.txt`).

## Project Structure
- `LanzadorConversor_4k.bat`: Windows UTF-8 launcher script (`chcp 65001`).
- `conversor_principal.py`: Main orchestrator managing folder iteration and batch execution.
- `configuracion.py`: Centralized binary paths, logging setup, and bitrate selection menu.
- `interaccion.py`: Interactive CLI menus for target bitrate, output resolution (`4K`/`1080p`/`720p`), and HDR tonemapping.
- `gestor_archivos.py`: Queue scanner, idempotent file filtering, and safe atomic file transfers (`os.replace`).
- `comprobacionVideos.py`: `mkvmerge` remuxing wrapper and `ffprobe` HDR/codec stream analyzer.
- `metadatos.py`: JSON metadata parser for duration, audio languages, and forced subtitle tracks.
- `procesamiento.py`: FFmpeg subprocess runner, regex telemetry parser, and NVENC pipeline builder.
- `calculoTiempos.py`: Object-oriented timers (`CronometroVideo`, `GestorTiempos`) for real-time ETA computation.
- `interfaz.py`: ANSI escape-code progress bar and multi-line console renderer.

## Requirements
- Python 3.8+ (`colorama`)
- FFmpeg & FFprobe (compiled with `libzimg` and `nvenc` support)
- MKVToolNix (`mkvmerge`)
- NVIDIA GPU with NVENC support (for hardware HEVC encoding)

## Quick Start
1. Install Python dependencies:
   ```bash
   pip install colorama
   ```
2. Update binary paths (`ffmpeg`, `ffprobe`, `mkvmerge`) in `configuracion.py` and `comprobacionVideos.py`.
3. Add target directory paths to `carpetas.txt` (one folder path per line).
4. Run `LanzadorConversor_4k.bat` or execute:
   ```bash
   python conversor_principal.py
   ```
