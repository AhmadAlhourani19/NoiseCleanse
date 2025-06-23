"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""

import time
from Backend import (
    config,
    audio_io,
    impulse_response,
    offline_deconvolution,
    live_deconvolution,
    plotting
)


def menu():
    print("\n===== NoiseCleanse CLI Menu =====")
    print("1. Generate & Record Impulse Response")
    print("2. Record Speech & Run Offline Deconvolution")
    print("3. Start Live Deconvolution")
    print("4. Plot Saved Signals")
    print("5. Exit")
    return input("Select an option (1-5): ")


def option_1_generate_ir():
    print("\n[1] Generate & Record Impulse Response")
    sweep = impulse_response.generate_sweep(config.FS, config.SWEEP_DURATION, config.FREQ_START, config.FREQ_END)
    audio_io.play_audio(config.SWEEP_FILE)
    response = audio_io.record_audio(config.RESPONSE_FILE, config.SWEEP_DURATION + 2, config.FS)
    ir = impulse_response.extract_ir(response, sweep, config.FS)
    ir_pre = impulse_response.preprocess_ir(ir, config.FS)
    print("Impulse Response Ready and Saved.")


def option_2_offline_deconv():
    print("\n[2] Record Speech & Run Offline Deconvolution")
    speech = audio_io.record_audio(config.SPEECH_FILE, duration=5, fs=config.FS)

    ir, fs_ir = audio_io.load_audio(config.IR_FILE, target_fs=config.FS)
    ir_pre = impulse_response.preprocess_ir(ir, config.FS)

    print("\nChoose deconvolution method:")
    print("  a. Tikhonov Regularization")
    print("  b. MMSE")
    method_choice = input("Select (a/b): ").strip().lower()
    method = "mmse" if method_choice == 'b' else "tikhonov"

    recovered = offline_deconvolution.offline_deconvolve(speech, ir_pre, config.FS, method=method)

    plotting.plot_time(recovered, config.FS, "Recovered Signal (Time Domain)")
    plotting.plot_freq(recovered, config.FS, "Recovered Signal (Frequency Domain)")


def option_3_live_deconv():
    print("\n[3] Starting Live Deconvolution")
    ir, fs_ir = audio_io.load_audio(config.IR_FILE, target_fs=config.FS)
    ir_pre = impulse_response.preprocess_ir(ir, config.FS)

    live_deconvolution.start_live_deconv(ir_pre, config.FS)

    print("Live deconvolution is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        live_deconvolution.stop_live_deconv()


def option_4_plot_signals():
    print("\n[4] Plot Saved Signals")
    print("Options:")
    print("  a. Sweep")
    print("  b. Room Response")
    print("  c. Impulse Response")
    print("  d. Speech")
    print("  e. Recovered Output")
    opt = input("Choose one (a–e): ").lower()

    lookup = {
        'a': config.SWEEP_FILE,
        'b': config.RESPONSE_FILE,
        'c': config.IR_FILE,
        'd': config.SPEECH_FILE,
        'e': config.RECOVERED_FILE
    }

    if opt in lookup:
        sig, fs = audio_io.load_audio(lookup[opt], target_fs=config.FS)
        plotting.plot_time(sig, fs, f"{opt.upper()} - Time Domain")
        plotting.plot_freq(sig, fs, f"{opt.upper()} - Frequency Domain")
    else:
        print("Invalid option.")


if __name__ == "__main__":
    print("NoiseCleanse CLI Application")

    while True:
        choice = menu()
        if choice == '1':
            option_1_generate_ir()
        elif choice == '2':
            option_2_offline_deconv()
        elif choice == '3':
            option_3_live_deconv()
        elif choice == '4':
            option_4_plot_signals()
        elif choice == '5':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice, please select 1-5.")
