function [rxcbs] = ch_decoder_conv(rxdemod)

    % Converte os bits recebidos para valores soft (de -1 a +1)
    % Aqui assumimos que rxdemod está em formato binário (0 ou 1).
    rxdecod = double(2 * rxdemod - 1);  % Conversão: 0 -> -1, 1 -> +1

    % Realiza a decodificação convolucional usando a função do MATLAB LTE
    rxcbs = lteConvolutionalDecode(rxdecod);

end
