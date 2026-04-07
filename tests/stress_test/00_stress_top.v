module stress_top (
    input wire clk,
    input wire rst_n,
    input wire [15:0] ext_in_a,
    input wire [15:0] ext_in_b,
    input wire [7:0] mode,
    output wire [31:0] debug_out,
    output wire [7:0] status_bus,
    output wire irq
);
    wire slow_clk_0;
    wire slow_clk_1;
    wire capture_flag;
    wire pulse_a;
    wire pulse_b;
    wire pulse_c;
    wire pulse_d;

    wire [15:0] seed0;
    wire [15:0] seed1;
    wire [15:0] seed2;
    wire [15:0] seed3;
    wire [15:0] pat0;
    wire [15:0] pat1;
    wire [15:0] pat2;
    wire [15:0] pat3;
    wire [15:0] noise0;
    wire [15:0] noise1;
    wire [15:0] twist0;
    wire [15:0] twist1;
    wire [15:0] sum0;
    wire [15:0] sum1;
    wire [15:0] fan0;
    wire [15:0] fan1;
    wire [15:0] cross0;
    wire [15:0] cross1;
    wire [15:0] lane0;
    wire [15:0] lane1;
    wire [15:0] lane2;
    wire [15:0] lane3;
    wire [15:0] filt0;
    wire [15:0] filt1;
    wire [15:0] fb0;
    wire [15:0] fb1;
    wire [15:0] state0;
    wire [15:0] state1;
    wire [15:0] route0;
    wire [15:0] route1;
    wire [15:0] route2;
    wire [15:0] route3;
    wire [15:0] stretch0;
    wire [15:0] stretch1;
    wire [15:0] arb0;
    wire [15:0] arb1;
    wire [15:0] reg0;
    wire [15:0] reg1;
    wire [15:0] hist0;
    wire [15:0] hist1;
    wire [15:0] cmp0;
    wire [15:0] cmp1;
    wire [15:0] scat0;
    wire [15:0] scat1;
    wire [15:0] vote0;
    wire [15:0] vote1;
    wire [15:0] delay0;
    wire [15:0] delay1;
    wire [15:0] chk0;
    wire [15:0] chk1;
    wire [15:0] ctrl0;
    wire [15:0] ctrl1;
    wire [15:0] gate0;
    wire [15:0] gate1;
    wire [15:0] pack0;
    wire [15:0] pack1;
    wire [7:0] flags0;
    wire [7:0] flags1;

    clock_div u_clock_div_0 (
        .clk(clk),
        .rst_n(rst_n),
        .slow_clk(slow_clk_0)
    );

    clock_div u_clock_div_1 (
        .clk(slow_clk_0),
        .rst_n(rst_n),
        .slow_clk(slow_clk_1)
    );

    async_capture u_async_capture (
        .clk(clk),
        .rst_n(rst_n),
        .async_a(ext_in_a[0]),
        .async_b(ext_in_b[0]),
        .capture(capture_flag)
    );

    seed_bank u_seed_bank (
        .clk(clk),
        .rst_n(rst_n),
        .in_a(ext_in_a),
        .in_b(ext_in_b),
        .mode(mode),
        .seed0(seed0),
        .seed1(seed1),
        .seed2(seed2),
        .seed3(seed3)
    );

    pattern_gen u_pattern_gen_0 (
        .clk(clk),
        .rst_n(rst_n),
        .seed(seed0),
        .step(mode),
        .pattern(pat0)
    );

    pattern_gen u_pattern_gen_1 (
        .clk(slow_clk_0),
        .rst_n(rst_n),
        .seed(seed1),
        .step({mode[3:0], mode[7:4]}),
        .pattern(pat1)
    );

    pattern_gen u_pattern_gen_2 (
        .clk(clk),
        .rst_n(rst_n),
        .seed(seed2),
        .step(mode ^ 8'h3C),
        .pattern(pat2)
    );

    pattern_gen u_pattern_gen_3 (
        .clk(slow_clk_1),
        .rst_n(rst_n),
        .seed(seed3),
        .step(mode + 8'h11),
        .pattern(pat3)
    );

    lfsr_noise u_lfsr_noise_0 (
        .clk(clk),
        .rst_n(rst_n),
        .inject(pat0[0] ^ pat1[1] ^ capture_flag),
        .noise(noise0)
    );

    lfsr_noise u_lfsr_noise_1 (
        .clk(slow_clk_0),
        .rst_n(rst_n),
        .inject(pat2[2] ^ pat3[3] ^ mode[0]),
        .noise(noise1)
    );

    bus_twister u_bus_twister_0 (
        .a(pat0),
        .b(noise0),
        .c(seed2),
        .sel(mode[1:0]),
        .y(twist0)
    );

    bus_twister u_bus_twister_1 (
        .a(pat1),
        .b(noise1),
        .c(seed3),
        .sel(mode[3:2]),
        .y(twist1)
    );

    multi_add u_multi_add_0 (
        .a(twist0),
        .b(pat2),
        .c(noise1),
        .d(seed1),
        .bias({8'h00, mode}),
        .sum(sum0)
    );

    multi_add u_multi_add_1 (
        .a(twist1),
        .b(pat3),
        .c(noise0),
        .d(seed0),
        .bias({mode, 8'h5A}),
        .sum(sum1)
    );

    fanin_reduce12 u_fanin_reduce12_0 (
        .in0(seed0), .in1(seed1), .in2(seed2), .in3(seed3),
        .in4(pat0), .in5(pat1), .in6(pat2), .in7(pat3),
        .in8(noise0), .in9(noise1), .in10(twist0), .in11(twist1),
        .out_word(fan0)
    );

    fanin_reduce12 u_fanin_reduce12_1 (
        .in0(sum0), .in1(sum1), .in2(fan0), .in3(noise0),
        .in4(noise1), .in5(pat0), .in6(pat1), .in7(pat2),
        .in8(pat3), .in9(seed0), .in10(seed2), .in11(seed3),
        .out_word(fan1)
    );

    cross_mix16 u_cross_mix16_0 (
        .in0(seed0), .in1(seed1), .in2(seed2), .in3(seed3),
        .in4(pat0), .in5(pat1), .in6(pat2), .in7(pat3),
        .in8(noise0), .in9(noise1), .in10(sum0), .in11(sum1),
        .in12(fan0), .in13(fan1), .in14(twist0), .in15(twist1),
        .sel(mode[3:0]),
        .mix_out(cross0)
    );

    cross_mix16 u_cross_mix16_1 (
        .in0(sum0), .in1(sum1), .in2(fan0), .in3(fan1),
        .in4(cross0), .in5(seed0), .in6(seed1), .in7(seed2),
        .in8(seed3), .in9(pat0), .in10(pat1), .in11(pat2),
        .in12(pat3), .in13(noise0), .in14(noise1), .in15(ext_in_a),
        .sel(mode[7:4]),
        .mix_out(cross1)
    );

    edge_mix u_edge_mix_0 (
        .clk(clk), .rst_n(rst_n), .left(cross0), .right(fan0), .sel(mode[1:0]), .mixed(lane0), .pulse(pulse_a)
    );
    edge_mix u_edge_mix_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .left(cross1), .right(fan1), .sel(mode[3:2]), .mixed(lane1), .pulse(pulse_b)
    );

    pipeline_lane u_pipeline_lane_0 (
        .clk(clk), .rst_n(rst_n), .din(lane0), .side(sum0), .lane_out(lane2)
    );
    pipeline_lane u_pipeline_lane_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .din(lane1), .side(sum1), .lane_out(lane3)
    );

    window_filter u_window_filter_0 (
        .clk(clk), .rst_n(rst_n), .din(lane2 ^ cross1), .coeff(mode[3:0]), .dout(filt0)
    );
    window_filter u_window_filter_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .din(lane3 + cross0), .coeff(mode[7:4]), .dout(filt1)
    );

    feedback_unit u_feedback_unit_0 (
        .clk(clk), .rst_n(rst_n), .forward_word(filt0), .return_word(lane3), .enable(mode[0]), .feedback_word(fb0)
    );
    feedback_unit u_feedback_unit_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .forward_word(filt1), .return_word(lane2), .enable(mode[1]), .feedback_word(fb1)
    );

    state_bank u_state_bank_0 (
        .clk(clk), .rst_n(rst_n), .load(mode[2]), .data_in(fb0 ^ fan1), .shadow_in(cross0), .state_out(state0)
    );
    state_bank u_state_bank_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .load(mode[3]), .data_in(fb1 ^ fan0), .shadow_in(cross1), .state_out(state1)
    );

    router_slice u_router_slice_0 (
        .in_word(state0), .side_word(fb1), .select(mode[1:0]), .route_word(route0)
    );
    router_slice u_router_slice_1 (
        .in_word(state1), .side_word(fb0), .select(mode[3:2]), .route_word(route1)
    );
    router_slice u_router_slice_2 (
        .in_word(route0 ^ lane2), .side_word(sum1), .select(mode[5:4]), .route_word(route2)
    );
    router_slice u_router_slice_3 (
        .in_word(route1 + lane3), .side_word(sum0), .select(mode[7:6]), .route_word(route3)
    );

    pulse_stretch u_pulse_stretch_0 (
        .clk(clk), .rst_n(rst_n), .pulse_in(pulse_a ^ pulse_b), .level_in(state0[3:0]), .stretched(stretch0), .pulse_out(pulse_c)
    );
    pulse_stretch u_pulse_stretch_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .pulse_in(pulse_b ^ capture_flag), .level_in(state1[3:0]), .stretched(stretch1), .pulse_out(pulse_d)
    );

    arbiter_tree u_arbiter_tree_0 (
        .req0(route0), .req1(route1), .req2(route2), .req3(route3), .mask(mode[3:0]), .grant(arb0)
    );
    arbiter_tree u_arbiter_tree_1 (
        .req0(stretch0), .req1(stretch1), .req2(fb0), .req3(fb1), .mask(mode[7:4]), .grant(arb1)
    );

    bus_register u_bus_register_0 (
        .clk(clk), .rst_n(rst_n), .en(mode[4]), .din(arb0 ^ route3), .dout(reg0)
    );
    bus_register u_bus_register_1 (
        .clk(slow_clk_1), .rst_n(rst_n), .en(mode[5]), .din(arb1 ^ route2), .dout(reg1)
    );

    histogram_core u_histogram_core_0 (
        .clk(clk), .rst_n(rst_n), .sample(reg0), .alt(reg1), .hist_out(hist0)
    );
    histogram_core u_histogram_core_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .sample(reg1), .alt(reg0), .hist_out(hist1)
    );

    compare_mesh u_compare_mesh_0 (
        .a(hist0), .b(hist1), .c(arb0), .d(arb1), .cmp_out(cmp0)
    );
    compare_mesh u_compare_mesh_1 (
        .a(route2), .b(route3), .c(state0), .d(state1), .cmp_out(cmp1)
    );

    scatter_switch u_scatter_switch_0 (
        .src0(cmp0), .src1(cmp1), .src2(hist0), .src3(hist1), .sel(mode[2:0]), .out_word(scat0)
    );
    scatter_switch u_scatter_switch_1 (
        .src0(route0), .src1(route1), .src2(route2), .src3(route3), .sel(mode[5:3]), .out_word(scat1)
    );

    vote_bank u_vote_bank_0 (
        .in0(scat0), .in1(scat1), .in2(cmp0), .in3(cmp1), .in4(hist0), .in5(hist1), .vote_out(vote0)
    );
    vote_bank u_vote_bank_1 (
        .in0(arb0), .in1(arb1), .in2(fb0), .in3(fb1), .in4(state0), .in5(state1), .vote_out(vote1)
    );

    delay_line u_delay_line_0 (
        .clk(clk), .rst_n(rst_n), .din(vote0), .tap0(delay0), .tap1()
    );
    delay_line u_delay_line_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .din(vote1), .tap0(delay1), .tap1()
    );

    checksum_merge u_checksum_merge_0 (
        .a(delay0), .b(delay1), .c(vote0), .d(vote1), .checksum(chk0)
    );
    checksum_merge u_checksum_merge_1 (
        .a(scat0), .b(scat1), .c(cmp0), .d(cmp1), .checksum(chk1)
    );

    wide_control u_wide_control_0 (
        .in0(seed0), .in1(seed1), .in2(seed2), .in3(seed3),
        .in4(pat0), .in5(pat1), .in6(pat2), .in7(pat3),
        .in8(chk0), .in9(chk1), .in10(vote0), .in11(vote1),
        .in12(scat0), .in13(scat1),
        .mode(mode),
        .ctrl_out(ctrl0)
    );

    wide_control u_wide_control_1 (
        .in0(route0), .in1(route1), .in2(route2), .in3(route3),
        .in4(arb0), .in5(arb1), .in6(hist0), .in7(hist1),
        .in8(cmp0), .in9(cmp1), .in10(delay0), .in11(delay1),
        .in12(fb0), .in13(fb1),
        .mode(mode ^ 8'hA7),
        .ctrl_out(ctrl1)
    );

    gate_cloud u_gate_cloud_0 (
        .a(ctrl0), .b(chk0), .c(vote0), .d(delay0), .y(gate0)
    );
    gate_cloud u_gate_cloud_1 (
        .a(ctrl1), .b(chk1), .c(vote1), .d(delay1), .y(gate1)
    );

    final_pack u_final_pack_0 (
        .a(gate0), .b(gate1), .c(ctrl0), .d(ctrl1), .pack(pack0)
    );
    final_pack u_final_pack_1 (
        .a(chk0), .b(chk1), .c(hist0), .d(hist1), .pack(pack1)
    );

    status_flags u_status_flags_0 (
        .clk(clk), .rst_n(rst_n), .sample0(pack0), .sample1(pack1), .sample2(gate0), .pulse_in(pulse_c), .flags(flags0), .irq()
    );
    status_flags u_status_flags_1 (
        .clk(slow_clk_0), .rst_n(rst_n), .sample0(ctrl0), .sample1(ctrl1), .sample2(gate1), .pulse_in(pulse_d), .flags(flags1), .irq(irq)
    );

    assign debug_out = {pack0[15:8] ^ pack1[7:0], ctrl0[15:8] ^ ctrl1[7:0], gate0[15:8] ^ gate1[7:0], chk0[15:8] ^ chk1[7:0]};
    assign status_bus = flags0 ^ flags1;
endmodule
