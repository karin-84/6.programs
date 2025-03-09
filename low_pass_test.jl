using FFTW
using DelimitedFiles
using Printf
using Statistics
using FileIO

# ==================================================

folder_path = "test_input\\"
save_path = "test_output"
time_interval = 1/60
cutoff_freq = 5.0

# ==================================================

function load_data_from_folder(folder_path)
    data_files = filter(f -> endswith(f, ".txt"), readdir(folder_path))
    all_data = Dict()
    
    for file in sort(data_files)
        file_path = joinpath(folder_path, file)
        println(file_path)
        data = readdlm(file_path)
        all_data[file] = data
    end
    
    return all_data
end

function perform_fft(velocity_data, time_interval)
    N = length(velocity_data)
    T = time_interval  # データ間隔（秒）
    freq = fftfreq(N, T)
    fft_values = fft(velocity_data)
    return freq, fft_values
end

function apply_lowpass_filter(freq, fft_values, cutoff)
    filtered_fft = copy(fft_values)
    for i in eachindex(fft_values)
        if abs(freq[i]) > cutoff
            filtered_fft[i] = 0.0
        end
    end
    return filtered_fft
end

function extract_common_prefix(filenames)
    if isempty(filenames)
        return "output"
    end
    prefix = reduce((x, y) -> x[1:min(length(x), length(y))] == y[1:min(length(x), length(y))] ? x[1:min(length(x), length(y))] : x[1:0], filenames)
    return rstrip(prefix, "_-.")
end

function main()
    all_data = load_data_from_folder(folder_path)
    common_prefix = extract_common_prefix(collect(keys(all_data)))
    output_folder_name = @sprintf("%.5fsec_lp%.2fHz_%s", time_interval, cutoff_freq, common_prefix)
    output_folder_path = joinpath(save_path, output_folder_name)
    mkpath(output_folder_path)
    
    for (file, data) in all_data
        if size(data, 2) < 5
            println("ファイル $file のデータ形式が不正です。")
            continue
        end
        
        velocity_data = data[:, 5]  # 速さデータを取得 (Juliaは1-indexedなので5番目はdata[:,5])
        freq, fft_values = perform_fft(velocity_data, time_interval)
        filtered_fft = apply_lowpass_filter(freq, fft_values, cutoff_freq)
        processed_velocity = real(ifft(filtered_fft))
        
        data[:, 5] = processed_velocity  # 速さ部分を更新
        output_file_path = joinpath(output_folder_path, @sprintf("%.5fsec_lp%.2fHz_%s", time_interval, cutoff_freq, file))
        writedlm(output_file_path, data)
        println("保存完了: $output_file_path")
    end
end

main()
