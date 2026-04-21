import math

def determinant_3x3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

def linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    denominator = n * sum_x2 - sum_x ** 2
    m = (n * sum_xy - sum_x * sum_y) / denominator
    b = (sum_y - m * sum_x) / n
    y_mean = sum_y / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    ss_res = sum((yi - (m * xi + b)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - (ss_res / ss_tot)
    return m, b, r2

def quadratic_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_x3 = sum(xi ** 3 for xi in x)
    sum_x4 = sum(xi ** 4 for xi in x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2y = sum((xi ** 2) * yi for xi, yi in zip(x, y))
    A = [[sum_x4, sum_x3, sum_x2], [sum_x3, sum_x2, sum_x], [sum_x2, sum_x, n]]
    det_A = determinant_3x3(A)
    A_a = [[sum_x2y, sum_x3, sum_x2], [sum_xy, sum_x2, sum_x], [sum_y, sum_x, n]]
    A_b = [[sum_x4, sum_x2y, sum_x2], [sum_x3, sum_xy, sum_x], [sum_x2, sum_y, n]]
    A_c = [[sum_x4, sum_x3, sum_x2y], [sum_x3, sum_x2, sum_xy], [sum_x2, sum_x, sum_y]]
    a = determinant_3x3(A_a) / det_A
    b = determinant_3x3(A_b) / det_A
    c = determinant_3x3(A_c) / det_A
    y_mean = sum_y / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    ss_res = sum((yi - (a * xi**2 + b * xi + c)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - (ss_res / ss_tot)
    return a, b, c, r2

if __name__ == "__main__":
    x = [2, 4, 2, 5, 4, 0, 3, 5, 1, 3]
    y = [137, 70, 184, 0, 35, 297, 122, 1, 253, 150]
    m, b, r2_lin = linear_regression(x, y)
    print(f"Linear: y = {m:.4f}x + {b:.4f}, R2 = {r2_lin:.4f}")
    aq, bq, cq, r2_quad = quadratic_regression(x, y)
    print(f"Quadratic: y = {aq:.4f}x^2 + {bq:.4f}x + {cq:.4f}, R2 = {r2_quad:.4f}")
