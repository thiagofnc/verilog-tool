module lfsr_noise (
    input wire clk,
    input wire rst_n,
    input wire inject,
    output reg [15:0] noise
);
    wire feedback_bit;

    assign feedback_bit = noise[15] ^ noise[13] ^ noise[12] ^ noise[10] ^ inject;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            noise <= 16'hA5C3;
        end else begin
            noise <= {noise[14:0], feedback_bit};
        end
    end
endmodule
