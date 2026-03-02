# Initial Material: Urban SAR Micro-Swarm (3-Unit System)

## 1) Mission Reframe and Constraints

This concept is strongest as a **humanitarian urban search-and-rescue (SAR)** system in GPS-denied buildings. Your latest constraints are locked in:

- `Unit 1: Carrier` (air or ground) moves assets to the operation area.
- `Unit 2: Observer` is a single aerial unit for top-level building understanding.
- `Unit 3: Swarm` is ~100 indoor units that clear buildings/floors, map interiors, and mark survivor locations.
- Swarm onboard compute target: **< $100 per drone**.
- Swarm should use LiDAR + object detection for survivor state cues.
- Swarm must form a self-healing mesh and auto-adjust positions to extend range in weak areas.

## 2) Important Design Correction (to improve your plan)

Two parts of the initial concept are technically risky if left unchanged:

- A **single observer very high above buildings** can become a resolution/comms bottleneck and single point of failure.
- Putting **full LiDAR on all 100 drones** is usually a poor cost/weight/power tradeoff.

Better approach while keeping your 3-unit architecture:

- Keep one observer, but operate near roofline orbit windows (not always max altitude) for useful building detail.
- Keep 100 swarm units, but make the swarm **heterogeneous**:
  - `60 Scout units`: camera + lightweight depth (ToF/stereo), low-cost AI compute.
  - `25 Mapper units`: add compact LiDAR for geometry-critical zones.
  - `15 Relay units`: prioritize mesh relay/perch endurance over heavy perception.

This keeps your intent and improves feasibility.

## 3) Compute Need Comparison (your key question)

### A) Indoor specialist swarm unit (scout/mapper role)

Reference modeling assumptions:

- Detector baseline: YOLO26 FLOPs table [S2].
- Indoor scout detector profile: small model, 320-480 input, 8-12 FPS.
- One-camera narrow-role perception + local navigation.

Estimated budget:

- Detection workload: ~0.01-0.08 TOPS effective.
- Navigation/control/mapping overhead: ~0.02-0.08 TOPS effective.
- Provisioned margin for real deployment: ~3x.
- **Provisioned target**: ~`0.1-0.3 TOPS` per swarm drone.

### B) Large all-domain drone (open + urban + indoor in one platform)

Representative assumptions:

- High-res multi-camera detection and tracking across open terrain + urban transitions.
- Example scaling from YOLO26m at 1280 and 2 cameras [S2].
- Additional global planning/fusion overhead for mixed-context mission.

Estimated budget:

- Detection alone can reach ~`8+ TOPS` equivalent in demanding settings.
- End-to-end mission stack typically pushes into `10-20+ TOPS` class.

### Bottom line

Indoor specialist per-node compute is typically **orders of magnitude lower** than one all-domain platform. In this model, the gap remains roughly **50x-200x** depending sensor load and latency targets.

## 4) Under-$100 Compute Strategy for Swarm Units

Target applies to onboard compute electronics (not full airframe/motors/battery).

### Candidate compute tiers

- `Tier L (~$14-$25)`:
  - RV1103 modules (e.g., LuckFox Pico Plus listed around $13.99-$14.99) [S7].
  - Good for low-res detection triggers and visual navigation assist.

- `Tier M (~$54-$70)`:
  - 1 TOPS class AI camera modules (e.g., reCamera 2002 listed at 53.90 EUR) [S8].
  - Better headroom for fused detection + local mapping.

- `Tier M+ optional`:
  - UWB module for better localization handoff (DWM3000 listed at $23.62) [S9].

Conclusion: `<$100` compute per swarm unit is feasible with careful part selection.

## 5) LiDAR Integration Without Breaking Cost/Weight

LiDAR on every unit is not optimal. Recommended:

- Add compact LiDAR primarily to mapper subgroup.
- Use cheaper depth sensing (ToF/stereo) on scout subgroup.
- Keep relay subgroup minimal to maximize endurance.

Reference LiDAR module baseline:

- TF-Luna class: <5 g, <=0.35 W, ~0.2-8 m spec [S10], retail reference ~$23.56 [S11].

## 6) Mesh Networking and Auto-Alignment

### Mesh foundation

- ESP-WIFI-MESH supports self-forming and self-healing behavior and large node counts in principle [S12][S13].
- Thread/BLE Mesh can be evaluated for lower-throughput roles [S14][S15].

### Auto-alignment behavior (practical)

Every 2-5 seconds each drone computes a link-health score to parent/peers:

- Inputs: RSSI/SNR, packet loss, queue delay, and hop count.
- If score drops below threshold, nearby relay-designated units reposition to restore margin.
- Prefer perch/hover waypoints to reduce energy burn from constant movement.

This creates dynamic corridor extension deeper into buildings.

## 7) Three-Unit Operational Flow

1. **Carrier stage**: Deploy observer + swarm canisters at perimeter.
2. **Observer stage**: Build coarse exterior/roof model, identify likely ingress points.
3. **Swarm stage**: Split by building/floor graph and clear zones in parallel.
4. **Detection stage**: Scouts trigger candidates, mappers verify geometry and route.
5. **Marker stage**: Closest unit lands/perches near survivor candidate and beacons location.
6. **Handoff stage**: Carrier/command node receives fused map + confidence-ranked targets and stores a reusable 3D mesh for future operations.

## 8) Recommended Next Build Step

Implement a simulation-first v0.1 with the exact 100-unit composition (`60/25/15`) and run sensitivity sweeps across:

- Detection FPS and input resolution.
- Mesh relay density.
- LiDAR penetration ratio (10%, 25%, 40%).
- Time-to-locate, false-alerts/hour, and battery-per-cleared-floor.

## References

See [SOURCES.md](./SOURCES.md).
