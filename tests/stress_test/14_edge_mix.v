module edge_mix (
    input wire clk,
    input wire rst_n,
    input wire [15:0] left,
    input wire [15:0] right,
    input wire [1:0] sel,
    output reg [15:0] mixed,
    output reg pulse
);
    reg [15:0] sampled_right;

    always @(negedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sampled_right <= 16'h0000;
        end else begin
            sampled_right <= right ^ {16{left[0]}};
        end
    end

    always @(*) begin
        case (sel)
            2'b00: mixed = left ^ sampled_right;
            2'b01: mixed = (left & sampled_right) | {left[7:0], sampled_right[7:0]};
            2'b10: mixed = (left | sampled_right) + 16'h0013;
            default: mixed = {left[4:0], sampled_right[15:5]} ^ 16'h5AA5;
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pulse <= 1'b0;
        end else begin
            pulse <= ^mixed;
        end
    end
endmodule
