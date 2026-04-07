module router_slice (
    input wire [15:0] in_word,
    input wire [15:0] side_word,
    input wire [1:0] select,
    output reg [15:0] route_word
);
    always @(*) begin
        if (select == 2'b00) begin
            route_word = in_word;
        end else if (select == 2'b01) begin
            route_word = {in_word[7:0], side_word[15:8]};
        end else if (select == 2'b10) begin
            route_word = (in_word ^ side_word) + 16'h0019;
        end else begin
            route_word = (in_word & side_word) | (in_word << 1);
        end
    end
endmodule
