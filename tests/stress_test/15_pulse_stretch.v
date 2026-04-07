module pulse_stretch (
    input wire clk,
    input wire rst_n,
    input wire pulse_in,
    input wire [3:0] level_in,
    output reg [15:0] stretched,
    output reg pulse_out
);
    reg [3:0] timer;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            timer <= 4'b0000;
            stretched <= 16'h0000;
            pulse_out <= 1'b0;
        end else begin
            if (pulse_in) begin
                timer <= level_in + 4'b0001;
            end else if (timer != 4'b0000) begin
                timer <= timer - 4'b0001;
            end
            stretched <= {8'h00, timer, level_in};
            pulse_out <= (timer != 4'b0000);
        end
    end
endmodule
