# Sources

Accessed: 2026-03-02

## Hardware and model benchmarks

- [S1] NVIDIA, "Jetson Orin" product page: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/
  - Used for: AGX Orin up to 275 TOPS (15W-60W), Orin NX up to 157 TOPS (10W-40W), Orin Nano up to 67 TOPS (7W-25W).

- [S2] Ultralytics, `README.md` (official repo): https://raw.githubusercontent.com/ultralytics/ultralytics/main/README.md
  - Used for: YOLO26 model FLOPs and speed table (for scaling compute budgets by resolution/FPS/model size).

- [S3] Bitcraze, "Crazyflie 2.1" specs: https://www.bitcraze.io/products/crazyflie-2-1/
  - Used for: Reference microdrone physical limits (27g total weight, ~15g recommended payload, up to ~7 min flight time).

- [S4] Bitcraze, "AI-deck 1.1": https://www.bitcraze.io/products/ai-deck/
  - Used for: Example low-power onboard AI stack (GAP8 + Himax camera + ESP32).

- [S5] GreenWaves Technologies, "GAP8 Processor": https://greenwaves-technologies.com/gap8_iot_application_processor/
  - Used for: Ultra-low-power edge-AI design point (vendor claims up to 300 GOPS/W in burst mode).

- [S6] DJI, "Matrice 30 Series Specifications" PDF: https://dl.djicdn.com/downloads/Matrice_30/20250828/Matrice_30_Series_Specifications_en.pdf
  - Used for: Representative larger platform baseline (max takeoff weight ~3770 g; max flight time up to 41 min in stated conditions).

## Low-cost compute, comms, and sensing references

- [S7] Waveshare, "LuckFox Pico Plus RV1103": https://www.waveshare.com/luckfox-pico-plus.htm
  - Used for: Example low-cost edge vision compute module with listed NPU and retail pricing ($13.99-$14.99).

- [S8] Gotronic, "reCamera 2002 8 GB": https://www.gotronic.fr/art-recamera-2022-8gb-47670.htm
  - Used for: Example 1 TOPS class AI camera module and retail pricing (53.90 EUR listed).

- [S9] Qorvo Store, "DWM3000 UWB module": https://store.qorvo.com/products/detail/dwm3000-qorvo/681949/
  - Used for: UWB module pricing reference ($23.62 at qty 1, with quantity breaks).

- [S10] Lumenier, "Benewake TF-Luna LiDAR": https://www.lumenier.com/products/benewake-tf-luna-lidar
  - Used for: TF-Luna size/weight/power reference (<5 g, <=0.35 W, 0.2-8 m).

- [S11] RobotShop, "Benewake TF-Luna 8m LiDAR": https://www.robotshop.com/products/benewake-tf-luna-8m-lidar-distance-sensor
  - Used for: TF-Luna retail pricing reference ($23.56 listed).

## Networking and architecture references

- [S12] Espressif, "ESP-WIFI-MESH overview": https://www.espressif.com/en/products/software/esp-mesh/overview
  - Used for: Self-forming, self-healing mesh claims and scale references (up to 1000 nodes).

- [S13] Espressif ESP-IDF docs, "ESP-WIFI-MESH": https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/esp-wifi-mesh.html
  - Used for: Relay behavior, root/intermediate/leaf concepts, and configurable layer/depth constraints.

- [S14] Espressif Techpedia, "Comparison of Different Mesh Solutions": https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/solution-introduction/mesh/mesh-comparison.html
  - Used for: Throughput/latency/node-count tradeoffs (ESP Mesh-Lite vs Thread).

- [S15] Bluetooth SIG, "Bluetooth Mesh FAQ": https://www.bluetooth.com/learn-about-bluetooth/feature-enhancements/mesh/mesh-faq/
  - Used for: Node-scale references and relay behavior in Bluetooth Mesh.

## Autonomy and perception context

- [S16] Cheng et al., "YOLC: You Only Look Clusters for Tiny Object Detection in Aerial Images," arXiv:2304.04466: https://arxiv.org/abs/2304.04466
  - Used for: Open-scene aerial tiny-object detection difficulty.

- [S17] Geethamani et al., "Novel Thermal-Based UAV Framework..." Drones 2025, 9(9), 625: https://www.mdpi.com/2504-446X/9/9/625
  - Used for: Thermal + deep-learning victim-detection context in emergencies.

- [S18] DARPA, "Fast Lightweight Autonomy (FLA)": https://www.darpa.mil/research/programs/fast-lightweight-autonomy
  - Used for: Fast navigation in unknown GPS/comms-denied environments.

- [S19] NIST UAS Indoor Mapping Challenge: https://www.nist.gov/el/intelligent-systems-division-73500/uav-indoor-mapping-challenge
  - Used for: Indoor GPS-denied mapping benchmark context.

- [S20] DJI Enterprise, "Mavic 3 Enterprise Specs": https://enterprise.dji.com/es/mavic-3-enterprise/specs
  - Used for: Observer-tier reference platform sizing and endurance (published enterprise specs).

## Market pricing references (indicative)

- [S21] Measur USA, "DJI Mavic 3 Enterprise": https://measurusa.com/products/dji-mavic-3
  - Used for: Example U.S. market price point ($3,628 listed when accessed).

- [S22] Benchmark Supply, "DJI Mavic 3 Enterprise": https://benchmarksupply.com/products/mavic-3-enterprise-1
  - Used for: Example U.S. market price point ($3,958 listed when accessed).

- [S23] Dronefly, "DJI Mavic 3 Enterprise": https://www.dronefly.com/products/dji-mavic-3-enterprise
  - Used for: Example U.S. market price point ($4,599 listed when accessed).

- [S24] Adorama, "DJI Mavic 3 Enterprise Bundle": https://www.adorama.com/djim3ewfpc.html
  - Used for: Example enterprise bundle pricing ($6,138 listed when accessed).

- [S25] CDW, "DJI MAVIC 3 THERMAL ENTERPRISE": https://www.cdw.com/product/dji-mavic-3-thermal-enterprise/7591793
  - Used for: Example thermal enterprise pricing ($5,174.99 listed when accessed).

- [S26] Adorama, "DJI Mavic 3 Thermal Advanced Bundle": https://www.adorama.com/djimavic3ta.html
  - Used for: Example thermal advanced bundle pricing ($6,599 listed when accessed).

- [S27] Waveshare, "ESP32-S3 product category": https://www.waveshare.com/product/arduino/boards-kits/esp32-s3.htm
  - Used for: Indicative ESP32-S3 dev-board pricing bands (examples in the $12.99-$13.99 range on listed SKUs).
