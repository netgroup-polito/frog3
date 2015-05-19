package utils.app_control;

public class RuleDefinitionClass {
	
	private String direction;
	private String macS;
	private String macD;
	private String ipS;
	private String ipD;
	private String tcpSP;
	private String tcpDP;
	private String udpSP;
	private String udpDP;
	
	public RuleDefinitionClass(String dir, String macS, String macD, String ipS, String ipD, String tcpSP, String tcpDP, String udpSP, String udpDP){
		
		this.setDirection(dir);
		this.setMacS(macS);
		this.setMacD(macD);
		this.setIpS(ipS);
		this.setIpD(ipD);
		this.setTcpSP(tcpSP);
		this.setTcpDP(tcpDP);
		this.setUdpSP(udpSP);
		this.setUdpDP(udpDP);
	}

	public String getDirection() {
		return direction;
	}

	public void setDirection(String direction) {
		this.direction = direction;
	}

	public String getMacS() {
		return macS;
	}

	public void setMacS(String macS) {
		this.macS = macS;
	}

	public String getMacD() {
		return macD;
	}

	public void setMacD(String macD) {
		this.macD = macD;
	}

	public String getIpS() {
		return ipS;
	}

	public void setIpS(String ipS) {
		this.ipS = ipS;
	}

	public String getIpD() {
		return ipD;
	}

	public void setIpD(String ipD) {
		this.ipD = ipD;
	}

	public String getTcpSP() {
		return tcpSP;
	}

	public void setTcpSP(String tcpSP) {
		this.tcpSP = tcpSP;
	}

	public String getTcpDP() {
		return tcpDP;
	}

	public void setTcpDP(String tcpDP) {
		this.tcpDP = tcpDP;
	}

	public String getUdpSP() {
		return udpSP;
	}

	public void setUdpSP(String udpSP) {
		this.udpSP = udpSP;
	}

	public String getUdpDP() {
		return udpDP;
	}

	public void setUdpDP(String udpDP) {
		this.udpDP = udpDP;
	}

}
