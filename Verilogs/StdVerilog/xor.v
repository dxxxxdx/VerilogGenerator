module xor_gate (
    input wire a,
    input wire b,
    output wire y
);

    wire or_out;
    wire and_out;

    or_gate u_or (
        .a(a),
        .b(b),
        .y(or_out)
    );

    and_gate u_and (
        .a(a),
        .b(b),
        .y(and_out)
    );

    assign y = or_out & ~and_out;

endmodule
