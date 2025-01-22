#import "@preview/lovelace:0.3.0": pseudocode-list
#set page(height: auto)
#set par(justify: true)
#set text(font: ("Libertinus Serif", "Noto Serif CJK SC"))
#set heading(numbering: "1.")
#let atan2 = math.op("atan2", limits: true)

= 筛选问题
对于二维度平面上的点$(x, y)$，其与$x$轴正方向夹角为 $atan2(y, x)$，取值范围是$(-pi, pi]$

对于一条线段，记其两端点分别为$a=(x_a, y_a, z_a), b=(x_b, y_b, z_b)$。

如果$x_b y_a = x_a y_b$（在二维平面上的投影直线经过原点）或者#text(fill: blue)[超出距离]就扔掉这个线段

$a, b$夹角分别为$ theta_a = atan2(y_a, x_a), quad theta_b = atan2(y_b, x_b) $
$theta_a, theta_b$的取值范围是$[-pi, pi]$。
不妨假设$theta_a < theta_b$，给定输入$theta in [0, pi)$，再做以下变换 $ (theta_a, theta_b, theta) = cases(
  (0, theta_b - theta_a, theta-theta_a) quad&"if" theta_b - theta_a < pi,
  (0, 2 pi + theta_a - theta_b, theta-theta_b) quad&"if" theta_b - theta_a > pi,
) $
此时$theta_a=0$，$theta_b in [0, pi)$。再对$theta$做以下变换：
$ theta = "fmod"("fmod"(theta, pi) + pi, pi) quad "// 属于" [0, pi) $

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

= 优化思路
== 删除无用线段
*Lemma 1:* 对于两条线段$A$和$B$，若$theta_1$和$theta_2$上都有$A >= B$，则$forall theta in [theta_1, theta_2]$也都有$A(theta) >= B(theta)$。

*Proof:* 记$A(theta) = a cos theta + b sin theta, quad B(theta) = c cos theta + d theta, quad A-B = (a-c) cos theta + (b-d) sin theta$。
$A-B$的相邻零点间隔是固定值$pi$，但线段的跨度必须小于$pi$，因此两个线段最多只有一个交点。
如果在两个端点都有$A>=B$，则$[theta_1, theta_2]$之间不存在$A<B$的点，否则会有两个交点。#sym.qed

根据*Lemma 1*，我们可以排除一部分必定不会成为最大值的线段：对于线段$A$和$B$，如果$B$的范围被$A$包括且$B<=A$在$B$的范围里总是成立，则$B$可以直接删除，只需要保留$A$。
这是一个找#text(fill: blue)[偏序集合中最大元]的问题。
需要找到一个时间复杂度小于$O(n log n)$的算法才能考虑使用。

== 分治算法
#figure(
kind: "algorithm",
supplement: [Algorithm],
pseudocode-list(booktabs: true, numbered-title: [计算线段分段最大值函数 #h(1fr)])[
+ *Input:* 一些线段的起点和终点 $cal(P) = {((theta^s_1, alpha^s_1), (theta^e_1, alpha^e_1)), dots, ((theta^s_n, alpha^s_n), (theta^e_n, alpha^e_n))}$
+ *Function* $cal(F)(cal(P))$
  + 找出 $cal(P)$ 中 $alpha$ 值最大的点 $p^* = (theta^*, alpha^*)$，记对应的线段为 $l^*$ #h(1fr) #text(fill: gray)[$O(n)$]
  + 计算所有线段与 $l^*$ 的交点中使得 $abs(theta^* - theta^')$ 最小的交点 $p^' = (theta^', alpha^')$ #h(1fr) #text(fill: gray)[$O(n)$]
  + $(theta_1, theta_2) <- (min(theta^*, theta^'), max(theta^*, theta^'))$
  + 对于横跨了 $theta_1$ 或 $theta_2$ 的线段，拆分成多条线段 #h(1fr) #text(fill: gray)[$O(n)$]
  + 将 $cal(P)$ 分出两个子集合 $cal(P)_1, cal(P)_2$ 分别表示在比 $theta_1$ 小和比 $theta_2$ 大的区域的线段 #h(1fr) #text(fill: gray)[$O(n)$]
  + *return* $cal(F)(P_1) + cal(f)(p^*, p^') + cal(F)(P_2)$
+ *end*
+ *Output:* $cal(F)(cal(P))$
]) <alg_divide>
对于输入的$n$条线段，@alg_divide 的时间复杂度为
$ T(n) = 2 T(n/2) + O(n) \
T(n) = O(n log n) $