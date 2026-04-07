module bus_register (
    input wire clk,
    input wire rst_n,
    input wire en,
    input wire [15:0] din,
    output reg [15:0] dout
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dout <= 16'h0000;
        end else if (en) begin
            dout <= din;
        end
    end
endmodule
