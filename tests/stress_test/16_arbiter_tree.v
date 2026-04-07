module arbiter_tree (
    input wire [15:0] req0,
    input wire [15:0] req1,
    input wire [15:0] req2,
    input wire [15:0] req3,
    input wire [3:0] mask,
    output reg [15:0] grant
);
    reg [15:0] left_pick;
    reg [15:0] right_pick;

    always @(*) begin
        left_pick = mask[0] ? req0 : (req0 | req1);
        right_pick = mask[1] ? req2 : (req2 ^ req3);

        if (mask[2]) begin
            grant = left_pick;
        end else if (mask[3]) begin
            grant = right_pick;
        end else begin
            grant = left_pick + right_pick;
        end
    end
endmodule
