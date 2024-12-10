function [txmod, locs] = modulate(data, M) %#codegen
    % A função modula os dados de entrada 'data' usando modulação QAM de ordem M
    % 'data' deve ser um vetor de bits, e M é a ordem da modulação 
    
    %locs = (data == -1);  % Identifica posições de dados que são -1, mas esta linha está comentada.
    %data(locs) = [];  % Remove dados com valor -1, caso fosse necessário. Comentado para não afetar o funcionamento.
    
    % Modulação QAM
    txmod = qammod(data, M, 'InputType', 'bit', 'UnitAveragePower', true);
end
