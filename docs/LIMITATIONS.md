# System Limitations & Boundary Conditions — LastMile Delivery Intelligence

## Known Limitations

1. **Static Traffic Representation**: The current public research datasets do not contain live high-frequency telemetry GPS ping streams; traffic factors are modeled via service time variance and historical travel durations.
2. **Geographic Scope**: Public datasets originate from U.S. metropolitan regions and specific European urban courier networks.
3. **No Live Production Dispatch Override**: The platform operates as a decision-intelligence overlay with human-in-the-loop audit logging; it does not directly control physical delivery vehicle hardware.
4. **Synthetic Data Policy Enforcement**: Synthetic data is used only for isolated UI edge cases when dataset files are not present in `./data/`. All evaluation metrics reported are calculated strictly on real datasets.
