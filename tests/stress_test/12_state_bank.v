module state_bank (
    input wire clk,
    input wire rst_n,
    input wire load,
    input wire [15:0] data_in,
    input wire [15:0] shadow_in,
    output reg [15:0] state_out
);
    reg [15:0] shadow;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_out <= 16'h55AA;
            shadow <= 16'hAA55;
        end else begin
            shadow <= shadow_in ^ {data_in[7:0], shadow_in[15:8]};
            if (load) begin
                state_out <= data_in + shadow;
            end else begin
                state_out <= state_out ^ shadow ^ {15'b0, data_in[0]};
            end
        end
    end
endmodule
