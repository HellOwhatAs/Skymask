#set text(font: ("Libertinus Serif", "Noto Serif CJK SC"))
#set heading(numbering: "1.")
#let atan2 = math.op("atan2", limits: true)

= 筛选问题
对于二位平面上的点$(x, y)$，其与$x$轴正方向夹角为 $atan2(y, x)$，取值范围是$(-pi, pi]$

对于一条线段，记其两端点分别为$a=(x_a, y_a, z_a), b=(x_b, y_b, z_b)$。
其夹角分别为$ theta_a = atan2(y_a, x_a), quad theta_b = atan2(y_b, x_b) $

对$theta_a, theta_b$以及输入$theta$做一步变换$ 
theta_((dot)) = cases(
  2 pi + theta_((dot)) quad&"if" theta_((dot)) < 0, 
  theta_((dot)) quad&"otherwise"
) $
这样$theta_a, theta_b$的取值范围就变成$[0, 2 pi)$了。不妨假设$theta_a < theta_b$，给定输入$theta in [0, pi)$，再做以下变换 $ (theta_a, theta_b, theta) = cases(
  (0, theta_b - theta_a, theta-theta_a) quad&"if" theta_b - theta_a < pi,
  (0, 2 pi + theta_a - theta_b, theta-theta_b) quad&"if" theta_b - theta_a > pi,
  (0, 0, 0) quad&"if" theta_b - theta_a = pi quad "// 不太合理",
) \
theta = "fmod"("fmod"(theta, pi) + pi, pi) quad "// 属于" [0, pi) $

筛选满足条件 $theta_a <= theta <= theta_b$ 的线段


= 仰角问题
给定输入角度$theta in (-pi, pi]$，
解得从原点出发与$x$轴正方向夹角为$theta$的射线与直线的交点坐标为
$ x = l cos theta \
y = l sin theta \
z = (y_a z_b - y_b z_a)/k cos theta + (x_b z_a - x_a z_b)/k sin theta $
其中 $ k = ((y_a-y_b) cos theta + (x_b - x_a) sin theta) \
l = ((x_b y_a - x_a y_b))/k $

则对于其仰角$alpha$有 $ tan(alpha) = z / l = ((y_a z_b - y_b z_a) cos theta + (x_b z_a - x_a z_b) sin theta)/(x_b y_a - x_a y_b) $

如果算出来是负数，说明是直线在相反方向，这样就可以将问题输入范围简化为$[0, pi)$

对于输入$theta in [0, pi)$，如果结果为正，则为 $theta$ 的值，而如果结果为负，则为负的$theta - pi$处的值

特殊情况：$(x_a, y_a)$、$(x_b, y_b)$与原点共线

记 $hat(alpha) = arctan(max(z_a/sqrt(x_a^2+y_a^2), z_b/sqrt(x_b^2+y_b^2)))$
+ 如果$atan2(y_a, x_a) = atan2(y_b, x_b) = theta $则
  $ alpha_(theta) = hat(alpha) $
+ 如果$atan2(y_a, x_a) = atan2(y_b, x_b) = theta - pi $则
  $ alpha_(theta-pi) = hat(alpha) $
+ 如果$atan2(y_a, x_a) = -atan2(y_b, x_b) $，这种情况意味着坐标原点在建筑物边缘上，不太合理
  // $ alpha_(theta) = alpha_(theta-pi) = pi/2 $