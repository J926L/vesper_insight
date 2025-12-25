use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct NetworkFlow {
    pub src_ip: String,
    pub dst_ip: String,
    pub src_port: u16,
    pub dst_port: u16,
    pub proto: String,
    pub timestamp: i64,
}

impl NetworkFlow {
    pub fn new(
        src_ip: String,
        dst_ip: String,
        src_port: u16,
        dst_port: u16,
        proto: String,
        timestamp: i64,
    ) -> Self {
        Self {
            src_ip,
            dst_ip,
            src_port,
            dst_port,
            proto,
            timestamp,
        }
    }
}
