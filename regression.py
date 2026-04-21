def determinant_3x3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

def quadratic_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_x3 = sum(xi ** 3 for xi in x)
    sum_x4 = sum(xi ** 4 for xi in x)
    
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2y = sum((xi ** 2) * yi for xi, yi in zip(x, y))

    A = [
        [sum_x4, sum_x3, sum_x2],
        [sum_x3, sum_x2, sum_x],
        [sum_x2, sum_x,  n]
    ]
    det_A = determinant_3x3(A)

    A_a = [
        [sum_x2y, sum_x3, sum_x2],
        [sum_xy,  sum_x2, sum_x],
        [sum_y,   sum_x,  n]
    ]
    A_b = [
        [sum_x4, sum_x2y, sum_x2],
        [sum_x3, sum_xy,  sum_x],
        [sum_x2, sum_y,   n]
    ]
    A_c = [
        [sum_x4, sum_x3, sum_x2y],
        [sum_x3, sum_x2, sum_xy],
        [sum_x2, sum_x,  sum_y]
    ]

    a = determinant_3x3(A_a) / det_A
    b = determinant_3x3(A_b) / det_A
    c = determinant_3x3(A_c) / det_A

    y_mean = sum_y / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    ss_res = sum((yi - (a * xi**2 + b * xi + c)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

    return r2

if __name__ == "__main__":
    x_data = [1, 2, 3, 4, 5, 6, 7]
    y_data = [2.1, 3.8, 6.5, 11.2, 17.5, 26.1, 36.8]
    r2 = quadratic_regression(x_data, y_data)
    # Output scaled to an integer for Clockwork
    final_output = int(r2 * 10000)
    print("R2:", final_output)
