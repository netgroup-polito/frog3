package utils.login;

public class HashTabValue {
	
	private String value1;
	private String value2;
	
	public HashTabValue(){
		super();
	}
	public HashTabValue(String v1, String v2){
		this.setValue1(v1);
		this.setValue2(v2);
	}

	public String getValue1() {
		return value1;
	}

	public void setValue1(String value1) {
		this.value1 = value1;
	}

	public String getValue2() {
		return value2;
	}

	public void setValue2(String value2) {
		this.value2 = value2;
	}

}
