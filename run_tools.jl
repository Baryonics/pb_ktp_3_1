module RunTools
        
    using DelimitedFiles, Revise
    using Base.Filesystem: isfile

    export run_binomial, run_interval, run_divide, read_txt_file


    function read_txt_file(file_path::String)
        if !isfile(file_path)
            error("File does not exist: $file_path")
        end
        data = readdlm(file_path, ' ')
        return data
    end


    function run_binomial(in_path::String, D_t::Float64, b::Int, out_path::String)
        run(`sh -c "python tools/binomial.py $in_path $D_t $b > $out_path"`)
        return read_txt_file(out_path)
    end


    function run_interval(in_path::String, D_t::Float64, c::Int64, out_path::String)
        run(`sh -c "python tools/interval.py $in_path $D_t $c > $out_path"`)
        return read_txt_file(out_path)
    end


    function run_divide(in_path::String, D_t::Float64, out_path::String)
        run(`sh -c "python tools/divide.py $in_path $D_t > $out_path"`)
        return read_txt_file(out_path)
    end
end