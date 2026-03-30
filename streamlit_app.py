import socket
import streamlit as st
from crc_input import append_crc, verify_packet

st.set_page_config(page_title="Data Monitor", layout="centered")

HOST = "127.0.0.1"
PORT = 12345

if "sock" not in st.session_state:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, PORT))
        st.session_state.sock, st.session_state.connected = s, True
    except:
        st.session_state.sock, st.session_state.connected = None, False

if "sent_log" not in st.session_state: st.session_state.sent_log = ""
if "recv_log" not in st.session_state: st.session_state.recv_log = ""
if "data_vals" not in st.session_state: st.session_state.data_vals = {}

st.write("### Decimal Input")
cols_in = st.columns(6)
inputs = [cols_in[i].number_input(f"In {i+1}", value=0, key=f"n{i}") for i in range(6)]

if st.button("Send Request"):
    if st.session_state.connected:
        try:
            packet = append_crc(bytes(inputs))
            st.session_state.sock.send(packet)
            st.session_state.sent_log = packet.hex().upper()
            
            resp = st.session_state.sock.recv(1024)
            st.session_state.recv_log = resp.hex().upper()
            
            if len(resp) >= 18:
                # CRC verify zaroori hai presentation ke liye
                _, _, valid = verify_packet(resp) 
                if valid:
                    st.session_state.data_vals = {
                        "HC": (resp[6] << 8) | resp[7],
                        "AS": (resp[8] << 8) | resp[9],
                        "CM": (resp[10] << 8) | resp[11],
                        "CP": (resp[12] << 8) | resp[13],
                        "CS": (resp[14] << 8) | resp[15],
                        "A1": resp[16], # Buffer 17
                        "A2": resp[17]  # Buffer 18
                    }
        except Exception as e:
            st.error(f"Comm Error: {e}")

st.write("---")
c1, c2 = st.columns(2)

with c1:
    st.write("**Alarms (1-16)**")
    d = st.session_state.data_vals
    # Dono bytes ko combine karke 16-bit banaya taaki loop chal sake
    combined_alarms = (d.get("A2", 0) << 8) | d.get("A1", 0)
    
    for i in range(16):
        status = "ON" if (combined_alarms >> i) & 1 else "OFF"
        # 8 ke baad ek divider taaki clear dikhe
        if i == 8: st.write("---") 
        st.text(f"Alarm {i+1}: {status}")

with c2:
    st.write("**Concentration**")
    for lbl, k in zip(["HS_Con", "AS_Con", "CM_Con", "CP_Con", "CS_Con"], ["HC", "AS", "CM", "CP", "CS"]):
        st.text(f"{lbl}: {d.get(k, '--')}")

st.write("---")
st.text(f"Sent: {st.session_state.sent_log}")
st.text(f"Data Received: {st.session_state.recv_log}")
