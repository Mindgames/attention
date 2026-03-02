# One-Pager: 3-Unit Urban SAR System (Value, Cost, Mesh, Comparisons)

Date: 2026-03-02  
Scope: Non-weaponized urban search-and-rescue (SAR) in GPS-denied buildings.

## 1) Executive Value

The proposed 3-unit system (Carrier + Observer + 100-drone indoor swarm) is valuable because it separates roles:

- High-level awareness from the observer.
- Deep indoor penetration from micro swarm units.
- Reliable command/logistics from the carrier.
- Swarm-fused telemetry builds high-quality 3D meshes that can be stored and reused in future operations.

This improves indoor coverage speed, failure tolerance, and comm resilience versus a single high-altitude autonomous drone trying to do every mission phase.

## 2) Cost Comparison (Core Ask)

All prices below are indicative market references captured on 2026-03-02.

### A) Single autonomous rescue drone from high altitude

- DJI Mavic 3 Enterprise listings: `$3,628` to `$4,599` [S21][S22][S23].
- Enterprise/thermal bundles: about `$5,174.99` to `$6,599` [S25][S26].

Practical hardware band for a single high-alt platform: **~$3.6k-$6.6k per unit** (before accessories, spare batteries, and operations kit).

### B) Indoor drone node with LiDAR + tiny model (10 classes max)

Reference BOM path (USD):

- Compute: LuckFox Pico Plus (RV1103) `$13.99-$14.99` [S7]
- LiDAR: TF-Luna `$23.56` [S11]
- Mesh board (ESP32-S3 dev board class): `$12.99-$13.99` [S27]
- Optional UWB ranging: `$17.18` at qty 100 (`$23.62` qty 1) [S9]

Per-drone electronics estimate:

- Without UWB: **~$50.54-$52.54**
- With UWB (bulk): **~$67.72-$69.72**
- With UWB (qty 1): **~$74.16-$76.16**

Conclusion: the LiDAR + tiny-model indoor node is materially cheaper than a high-alt autonomous enterprise drone, and can stay within a `<$100` onboard compute+sensor budget.

## 3) Compute and Model Scope (10-object detector)

- Limiting detection to 10 classes reduces output head complexity and false positives.
- Main compute drivers are still resolution, FPS, and camera count.
- For indoor short-range use, tiny models at 320-480 input and 8-12 FPS remain a strong fit.

Engineering guidance:

- Keep scouts at low-resolution, event-driven inference.
- Reserve heavier mapping load for mapper subgroup.
- Do not design all 100 units as identical LiDAR-heavy nodes.

## 4) Mesh Strategy (What makes it work indoors)

Base stack:

- ESP-WIFI-MESH for self-forming/self-healing behavior [S12][S13].

Control policy:

- Each node computes link score from RSSI/SNR, packet loss, queue delay, and hop count.
- If score falls below threshold, nearby relay-class units reposition to restore margin.
- Use perch points to reduce power drain vs continuous hovering.

Bandwidth policy:

- Scouts: event-first telemetry.
- Mappers: periodic compressed geometry updates.
- Relays: backbone first, payload second.

Data product:

- Multi-unit map fusion produces persistent 3D building meshes (floors, obstacles, viable paths) for future mission planning and responder rehearsals.

## 5) Comparability to Other Methods

| Method | Upfront hardware cost | Indoor coverage quality | Comms resilience indoors | Failure tolerance | Best use |
| --- | --- | --- | --- | --- | --- |
| Single high-alt autonomous drone | ~`$3.6k-$6.6k` per unit [S21-S23, S25-S26] | Medium for indoor (line-of-sight constrained) | Medium-Low | Low (single point of failure) | Fast exterior scan |
| Proposed 3-unit + 100 swarm | Swarm nodes ~`$51-$76` electronics each + observer/carrier [S7, S9, S11, S27] | High (parallel floor clearing) | High (self-healing mesh + relay motion) | High (many-node redundancy) | Full urban SAR workflow |
| Ground-robot-heavy approach | Variable, often higher per unit | Medium-High on reachable floors | Medium | Medium | Debris-heavy reachable corridors |
| Manual teams only | Lower hardware, higher personnel risk/time | Medium (depends on access) | N/A digital mesh | Medium | Traditional baseline and confirmation |

## 6) Decision

If the objective is fast indoor survivor search in dense urban structures, the strongest value/cost tradeoff is a heterogeneous 100-node swarm under the 3-unit architecture, not a single high-altitude autonomous drone.

## References

- [S7] https://www.waveshare.com/luckfox-pico-plus.htm
- [S9] https://store.qorvo.com/products/detail/dwm3000-qorvo/681949/
- [S11] https://www.robotshop.com/products/benewake-tf-luna-8m-lidar-distance-sensor
- [S12] https://www.espressif.com/en/products/software/esp-mesh/overview
- [S13] https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/esp-wifi-mesh.html
- [S21] https://measurusa.com/products/dji-mavic-3
- [S22] https://benchmarksupply.com/products/mavic-3-enterprise-1
- [S23] https://www.dronefly.com/products/dji-mavic-3-enterprise
- [S25] https://www.cdw.com/product/dji-mavic-3-thermal-enterprise/7591793
- [S26] https://www.adorama.com/djimavic3ta.html
- [S27] https://www.waveshare.com/product/arduino/boards-kits/esp32-s3.htm
