function [txcoded] = ch_coder_conv(txcbs)

    % Realiza a codificação convolucional usando a função do MATLAB LTE
    txcoded = lteConvolutionalEncode(txcbs);

end
