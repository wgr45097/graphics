# 《图形学大作业：离线全局光照明》代码运行步骤说明

## 第一步：构建Mitsuba Docker镜像
基于 https://github.com/Traverse-Research/mitsuba-conda-docker 提供的Dockerfile，构建Mitsuba Docker镜像。

我们实际运行后发现，默认使用GCC并开启O1或更高优化选项编译得到的Mitsuba运行经常崩溃。经过排查，我们猜测这是Mitsuba使用了C++的UB（未定义行为），而GCC的编译优化处理UB时比较激进。我们修改了Mitsuba编译脚本，换用LLVM编译器（参见 https://github.com/wgr45097/mitsuba/tree/scons-python3 ），使用O2编译优化选项，问题得到解决。

## 第二步：启动JSON Server
```bash
cd log-server
npx json-server db.json
```

在log-server目录下，我们使用一个JSON Server监听db.json，后续的实验驱动脚本每跑完一次测试就通过JSON Server向db.json插入一个日志条目，记录本次测试的运行时间、算法、场景、结果等信息。

## 第三步：运行实验驱动脚本
```bash
python3 run_mitsuba.py
```

实验驱动脚本`run_mitsuba.py`中可以设置多个integrators和多个scenes，脚本多次使用`docker run`运行第一步构建的Mitsuba Docker镜像，每次运行完成后将结果图片移动到`./output/`目录下并记录日志。

## 第四部：绘制MSE曲线
```bash
python3 compare_integrators.py
```

针对每个场景，该脚本在`./saved_pics/`目录下绘制不同算法的MSE-时间曲线，其中的运行时间信息通过访问JSON Server来获取。
