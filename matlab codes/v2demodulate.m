function [rxdemod] = demodulate(rxsig, M) %#codegen
% Função para demodular um sinal recebido utilizando modulação QAM.

    % Realiza a demodulação QAM, retornando os bits
    % 'UnitAveragePower', true: normaliza a potência média do sinal
    rxdemod = qamdemod(rxsig, M, 'OutputType', 'bit', 'UnitAveragePower', true);

    % Caso precise retornar os símbolos em vez de bits, use a seguinte linha:
    % rxdemod = qamdemod(rxsig, M, 'UnitAveragePower', true);
end
