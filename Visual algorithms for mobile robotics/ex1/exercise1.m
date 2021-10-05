clear;
close all;

undistorted_img = imread("data/images_undistorted/img_0001.jpg");
distorted_image = imread("data/images/img_0001.jpg");

undistorted_gray = rgb2gray(undistorted_img);
distorted_gray = rgb2gray(distorted_image);

K = readmatrix("data/K.txt");
poses = readmatrix("data/poses.txt");
% D = readmatrix("data/D.txt"); todo: read k1 and k2 from D.txt
k1 = -1.6774e-06;
k2 = 2.5847e-12;

% part 2.2
dx = 4; dy = 4;
x = 0:dx:32;
y = 0:dy:20;
z = 0;
[x_w, y_w, z_w] = meshgrid(x,y,z); %x, y, z world coordinates
[R, t] = poseVectorToTransformationMatrix(poses);
[U, V] = projectEdges(R, x_w, y_w, z_w, t, K, k1, k2, false);

subplot(2,2,1), imshow(undistorted_gray);
hold on;
scatter(U, V, 'filled');

% part 2.3
cube_size = 8;
cube_init = [0 0 0];
[cube_xs, cube_ys, cube_zs] = getCubeMatrix(cube_size, cube_init);
[cube_U, cube_V] = projectCube(cube_xs, cube_ys, cube_zs, R, t, K, k1, k2, false);

subplot(2,2,2), imshow(undistorted_gray); 
hold on;
DrawCube(cube_U, cube_V);

% part 2.4
% todo

% part 3.2
[U, V] = projectEdges(R, x_w, y_w, z_w, t, K, k1, k2, true);

subplot(2,2,3), imshow(distorted_gray);
hold on;
scatter(U, V, 'filled');

%part 3.3
[undistorted_image] = undistort_image(R, t, K, k1, k2, distorted_gray);
subplot(2,2,4), imshow(undistorted_image);
hold on;


function [undistorted_image] = undistort_image(R, t, K, k1, k2, distorted_image)
[width, height, depth] = size(distorted_image);
undistorted_image = uint8(zeros(width, height));
for i=1:width
   for j = 1:height
       [ud, vd] = distort_coordinates(i, j, K, k1, k2);
       u1 = floor(ud);
       v1 = floor(vd);
       a = ud-u1;
       b = vd-v1;
       if u1+1 > 0 && u1+1 <= width && v1+1 > 0 && v1+1 <= height
           undistorted_image(i,j) = (1-b) * ((1-a)*distorted_image(u1,v1) + a*distorted_image(u1,v1+1)) ...
               + b * ((1-a)*distorted_image(u1+1,v1) + a*distorted_image(u1+1,v1+1));
       end
       % undistorted_image(i, j) = distorted_image(u1, v1);
   end
end
end


function [] = DrawCube(cube_U, cube_V)
plot([cube_U(1) cube_U(2)], [cube_V(1) cube_V(2)],'Color','r','LineWidth',2);
plot([cube_U(2) cube_U(3)], [cube_V(2) cube_V(3)],'Color','r','LineWidth',2);
plot([cube_U(3) cube_U(4)], [cube_V(3) cube_V(4)],'Color','r','LineWidth',2);
plot([cube_U(1) cube_U(4)], [cube_V(1) cube_V(4)],'Color','r','LineWidth',2);
plot([cube_U(5) cube_U(6)], [cube_V(5) cube_V(6)],'Color','r','LineWidth',2);
plot([cube_U(6) cube_U(7)], [cube_V(6) cube_V(7)],'Color','r','LineWidth',2);
plot([cube_U(7) cube_U(8)], [cube_V(7) cube_V(8)],'Color','r','LineWidth',2);
plot([cube_U(5) cube_U(8)], [cube_V(5) cube_V(8)],'Color','r','LineWidth',2);
plot([cube_U(5) cube_U(1)], [cube_V(5) cube_V(1)],'Color','r','LineWidth',2);
plot([cube_U(6) cube_U(2)], [cube_V(6) cube_V(2)],'Color','r','LineWidth',2);
plot([cube_U(7) cube_U(3)], [cube_V(7) cube_V(3)],'Color','r','LineWidth',2);
plot([cube_U(8) cube_U(4)], [cube_V(8) cube_V(4)],'Color','r','LineWidth',2);
end


function [cube_xs, cube_ys, cube_zs] = getCubeMatrix(cube_size, cube_init)
cube_xs = [cube_init(1) cube_init(1) cube_init(1) cube_init(1) cube_init(1)+cube_size cube_init(1)+cube_size cube_init(1)+cube_size cube_init(1)+cube_size];
cube_ys = [cube_init(2) cube_init(2)+cube_size cube_init(2)+cube_size cube_init(2) cube_init(2) cube_init(2)+cube_size cube_init(2)+cube_size cube_init(2)];
cube_zs = [cube_init(3) cube_init(3) cube_init(3)-cube_size cube_init(3)-cube_size cube_init(3) cube_init(3) cube_init(3)-cube_size cube_init(3)-cube_size];
end


function [U, V] = projectCube(cube_xs, cube_ys, cube_zs, R, t, K, k1, k2, distortion)
U = []; V = [];
for i = 1:length(cube_xs)
    x = cube_xs(i)/100; y = cube_ys(i)/100; z = cube_zs(i)/100;
    [u, v] = projectPoint(R, x, y, z, t, K, k1, k2, distortion);
    U = [U u]; V = [V v];
end
end


function [U, V] = projectEdges(R, x_w, y_w, z_w, t, K, k1, k2, distortion)
[rows, columns, height] = size(x_w);
U = []; V = [];
for i = 1:rows
    for j = 1:columns
        for k = 1:height
            x = x_w(i,j,k)/100; y = y_w(i,j,k)/100; z = z_w(i,j,k)/100;
            [u, v] = projectPoint(R, x, y, z, t, K, k1, k2, distortion);
            U = [U u]; V = [V v];
        end
    end
end
end


function [u, v] = projectPoint(R, x, y, z, t, K, k1, k2, distortion)
if distortion
    [u_mapped, v_mapped] = map_world_to_image(K, R, t, x, y, z);
    [ud, vd] = distort_coordinates(u_mapped, v_mapped, K, k1, k2);
    u = ud; % just to return values
    v = vd; % just to return values
else
    [u,v] = map_world_to_image(K, R, t, x, y, z);
end
end


function [u, v] = map_world_to_image(K, R, t, x, y, z)
Img_frame = K*[R t]*[x; y; z; 1];
Img_frame = Img_frame/Img_frame(3);
u = Img_frame(1);
v = Img_frame(2);
end


function [ud, vd] = distort_coordinates(u_mapped, v_mapped, K, k1, k2)
u0 = K(1,3);
v0 = K(2,3);
r_square = (u_mapped - u0)*(u_mapped - u0) + (v_mapped - v0)*(v_mapped - v0);
points_delta = [(u_mapped - u0); (v_mapped - v0)];
optical_center = [u0; v0];
factor = (1 + k1*r_square + k2*(r_square^2));
Pd_init = factor * points_delta;
Pd = Pd_init + optical_center;
ud = Pd(1);
vd = Pd(2);
end


function [R, t] = poseVectorToTransformationMatrix(poses)
wx = poses(1,1); wy = poses(1,2); wz = poses(1,3);
tx = poses(1,4); ty = poses(1,5); tz = poses(1,6);
w = transpose([wx wy wz]);
t = transpose([tx ty tz]);
k = w/norm(w);
k_cross = [0 -k(3) k(2); k(3) 0 -k(1); -k(2) k(1) 0];
theta = norm(w);
R = eye(3) + sin(theta)*k_cross + (1-cos(theta))*(k_cross*k_cross);
end
