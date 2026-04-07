module pipeline_lane (
    input wire clk,
    input wire rst_n,
    input wire [15:0] din,
    input wire [15:0] side,
    output reg [15:0] lane_out
);
    reg [15:0] stage0;
    reg [15:0] stage1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            stage0 <= 16'h0000;
            stage1 <= 16'h0000;
            lane_out <= 16'h0000;
        end else begin
            stage0 <= din ^ side;
            stage1 <= stage0 + {side[7:0], side[15:8]};
            lane_out <= stage1 ^ {stage0[0], stage0[15:1]};
        end
    end
endmodule
