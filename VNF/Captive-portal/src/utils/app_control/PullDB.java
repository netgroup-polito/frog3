package utils.app_control;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.Date;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import utils.login.HashTabValue;

import com.google.gson.Gson;

/**
 * Servlet implementation class PullDB
 */
@WebServlet("/PullDB")
public class PullDB extends HttpServlet {
	private static final long serialVersionUID = 1L;
	public static Hashtable<Integer, HashTabValue> tableTemp= new Hashtable<Integer, HashTabValue>();
    /**
     * @see HttpServlet#HttpServlet()
     */
    public PullDB() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "unchecked", "rawtypes" })
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		System.out.println("INFO: Executing servlet_PullDB...");
		PrintWriter out = response.getWriter();
		
		//Session s=(Session)request.getAttribute("Session");
		
		
		//String user=request.getParameter("username");
		String priority=request.getParameter("priority");
		String username=request.getParameter("username");
		
		RuleDefinitionClass[] rule_list= new Gson().fromJson(request.getParameter("rule_list"),RuleDefinitionClass[].class);
		
		for(RuleDefinitionClass ll:rule_list){
			System.out.println(ll.getDirection());
		}
		
	
		
		ServletContext context = getServletContext();
		Hashtable<Integer, HashTabValue> idPex=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab");
		
		//Hashtable<Integer, HashTabValue> idPexHS=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTabHS");
		
		
		HashTabValue temp1= new HashTabValue(username, priority);
		int contatore=0;
		int tempID=0;
		
		Map<Integer,HashTabValue> sortedMap=null;
		if(idPex!=null){
		sortedMap= new TreeMap<Integer, HashTabValue>(idPex);
		}else{
			idPex=tableTemp;
			sortedMap= new TreeMap<Integer, HashTabValue>(idPex);
		}
		
		
		if(idPex.isEmpty()){
			tempID=1;
			idPex.put(tempID, temp1);//MAC no username here
			System.out.println("Hashmap vuota");
			this.getServletContext().setAttribute("HashTab2", idPex);
		}else{
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			tempID++;
			while(it.hasNext()){
				tempID++;
				contatore++;
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				
				
				if(!m.getKey().equals(contatore)){
					System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				tempID=contatore;
				break;
			}
				
				
				mm=(HashTabValue)m.getValue();
				System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			System.out.println("TempID: "+tempID+" contatore"+contatore);
			idPex.put(tempID, temp1);
			
		}
		
		
		
		
		Set ss=idPex.entrySet();
		Iterator it=ss.iterator();
		
		while(it.hasNext()){
			
			
			
			Map.Entry m=(Map.Entry)it.next();
			HashTabValue mm=new HashTabValue();
			
			mm=(HashTabValue)m.getValue();
			
				System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
		}
		
		
		String string_out=new String();
		string_out+="{";
		
		string_out+="\"command\" : \"new_slice\",";
		string_out+="\"pex\" : \""+tempID+"\",";
		string_out+="\"priority\" : \""+priority+"\",";
		
		string_out+="\"rules\" : [  ";
		
		int cont=0, cont2=0;
		cont=rule_list.length;
		for(RuleDefinitionClass rdc: rule_list){//
			cont2++;
			string_out+="{";
			string_out+="\"direction\" : \""+rdc.getDirection()+"\",";
		
		if(!rdc.getMacS().equals("*")){
				if(!rdc.getMacD().equals("*")||!rdc.getIpS().equals("*")||!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"eth_src\" : \""+rdc.getMacS()+"\",";
				}else{
					string_out+="\"eth_src\" : \""+rdc.getMacS()+"\"";
				}
			}
			if(!rdc.getMacD().equals("*")){
				if(!rdc.getIpS().equals("*")||!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"eth_dst\" : \""+rdc.getMacD()+"\",";
				}else{
					string_out+="\"eth_dst\" : \""+rdc.getMacD()+"\"";
				}
			}
			if(!rdc.getIpS().equals("*")){
				if(!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"ip_src\" : \""+rdc.getIpS()+"\",";
				}else{
					string_out+="\"ip_src\" : \""+rdc.getIpS()+"\"";
				}
			}
			if(!rdc.getIpD().equals("*")){
				if(!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"ip_dst\" : \""+rdc.getIpD()+"\",";
				}else{
					string_out+="\"ip_dst\" : \""+rdc.getIpD()+"\"";
				}
			}
			if(!rdc.getTcpSP().equals("*")){
				if(!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"tcp_src\" : \""+rdc.getTcpSP()+"\",";
				}else{
					string_out+="\"tcp_src\" : \""+rdc.getTcpSP()+"\"";
				}
			}
			if(!rdc.getTcpDP().equals("*")){
				if(!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"tcp_dst\" : \""+rdc.getTcpDP()+"\",";
				}else{
					string_out+="\"tcp_dst\" : \""+rdc.getTcpDP()+"\"";
				}
			}
			if(!rdc.getUdpSP().equals("*")){
				if(!rdc.getUdpDP().equals("*")){
				string_out+="\"udp_src\" : \""+rdc.getUdpSP()+"\",";
				}else{
					string_out+="\"udp_src\" : \""+rdc.getUdpSP()+"\"";
				}
			}
			if(!rdc.getUdpDP().equals("*")){
				string_out+="\"udp_dst\" : \""+rdc.getUdpDP()+"\"";
			}
			
			
			if(cont!=cont2){
			string_out+="},";
			}else{
				string_out+="}";
			}
		}
		string_out+="],";
		string_out+="\"type\" : \"horizontal\"";
		
		
		string_out+="}";
		
		System.out.println(string_out);
		
		/*Socket so=new Socket("127.0.0.1", 2525);
		DataOutputStream os= new DataOutputStream(so.getOutputStream());
		
		os.write(string_out.getBytes(Charset.forName("UTF-8")));
		
		
		
		
		os.close();
		
		so.close();*/
		
		
		out.print("{success:true}");
		
		System.out.println("Stiamo ricevendo i dati:");
		System.out.println("INFO: ...servlet_PullDB executed.");
		//System.out.println("Dati ricevuti: "+user);
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "rawtypes", "unchecked" })
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_PullDB...");
		PrintWriter out = response.getWriter();
		//int updateSlice=0;
		//Session s=(Session)request.getAttribute("Session");
		
		
		//String user=request.getParameter("username");
		String priority=request.getParameter("priority");
		String username=request.getParameter("username");
		String timestamp=request.getParameter("timestamp");
		System.out.println(new Date());
		System.out.println("--------------"+priority+" "+username+" "+timestamp);
		RuleDefinitionClass[] rule_list= new Gson().fromJson(request.getParameter("rule_list"),RuleDefinitionClass[].class);
		
		for(RuleDefinitionClass ll:rule_list){
			System.out.println(ll.getDirection());
		}
		
	
		
		ServletContext context = getServletContext();
		Hashtable<Integer, HashTabValue> idPex=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab");
		
		//Hashtable<Integer, HashTabValue> idPexHS=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTabHS");
		
		
		
		
		HashTabValue temp1= new HashTabValue(username, priority);
		int contatore=0;
		int tempID=0;
		
		Map<Integer,HashTabValue> sortedMap=null;
		if(idPex!=null){
			
			sortedMap= new TreeMap<Integer, HashTabValue>(idPex);
			
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			
			while(it.hasNext()){
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				mm=(HashTabValue)m.getValue();
				
				
				if(mm.getValue1().equals(username)&&mm.getValue2().equals(priority)){//per evitare rimozione PEX inserire controllo con TIMESTAMP
					
					//Dobbiamo eliminare la cartella pexID perchè stiamo aggiornando la slice Horizzonatale
					
					/*
					File TScontrol = new File("HSdump.txt");
					FileWriter fww = new FileWriter(TScontrol, true);
					fww.close();
					BufferedReader br2 = new BufferedReader(new FileReader(TScontrol));
					String lineControl;
					while((lineControl= br2.readLine())!=null){
						System.out.println("CONTROLLO="+lineControl);
						//System.out.println("LINEA STAMPATA:"+line+":FINE LINEA");
						if((lineControl.contains("\"pex\" : \""+m.getKey()+"\""))){
							System.out.println("Settiamo remove Slice");
							
							if(lineControl.contains("timestamp="+timestamp)){
							updateSlice=1;
							}else{
								System.out.println("VALORE TROVATO chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
								idPex.remove(m.getKey());
								/*String stringRemove="{\"command\" : \"remove_pex\",\"pex\" : \""+m.getKey()+"\"}";
								Socket so=new Socket("127.0.0.1", 2525);
								DataOutputStream os= new DataOutputStream(so.getOutputStream());
								
								os.write(stringRemove.getBytes(Charset.forName("UTF-8")));
								
								
								
								
								os.close();
								
								so.close();*/
				/*			}
						}else{
							
						}
					}
					
					br2.close();*/
					
					//associato qua una remove pex sul router
					
				}
				
				System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			sortedMap= new TreeMap<Integer, HashTabValue>(idPex);
		}else{
			idPex=tableTemp;
			sortedMap= new TreeMap<Integer, HashTabValue>(idPex);
		}
		
		//if(updateSlice==0){
		if(idPex.isEmpty()){
			tempID=1;
			idPex.put(tempID, temp1);//MAC no username here
			System.out.println("Hashmap vuota");
			this.getServletContext().setAttribute("HashTab2", idPex);
		}else{
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			tempID++;
			while(it.hasNext()){
				tempID++;
				contatore++;
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				
				
				if(!m.getKey().equals(contatore)){
					System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				tempID=contatore;
				break;
			}
				
				
				mm=(HashTabValue)m.getValue();
				System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			System.out.println("TempID: "+tempID+" contatore"+contatore);
			idPex.put(tempID, temp1);
			
		}
		
		
		
		
		Set ss=idPex.entrySet();
		Iterator it=ss.iterator();
		
		while(it.hasNext()){
			
			
			
			Map.Entry m=(Map.Entry)it.next();
			HashTabValue mm=new HashTabValue();
			
			mm=(HashTabValue)m.getValue();
			
				System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
		}
		
		
		String ConfPath=(String) request.getAttribute("ConfigurationFile");
		File fileXML = new File(ConfPath+"FrogRelativePath.xml");
		DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
		DocumentBuilder dBuilder;
		Document doc=null;
		try {
			dBuilder = dbFactory.newDocumentBuilder();
			doc = dBuilder.parse(fileXML);
		} catch (ParserConfigurationException e1) {
			e1.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		}
		
		doc.getDocumentElement().normalize();
		
		NodeList nodes1 = doc.getElementsByTagName("absolute_path_frog");
		Node node1 = nodes1.item(0);
		Element element1 = (Element) node1;
		NodeList nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
		Node node3 = (Node) nodes3.item(0);
		String line3=node3.getNodeValue();

		NodeList nodes = doc.getElementsByTagName("temp_pex_path");
		Node node = nodes.item(0);
		Element element = (Element) node;
		NodeList nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		Node node2 = (Node) nodes2.item(0);
		String line=node2.getNodeValue();
		
		
		/*
		InputStream in = getClass().getClassLoader().getResourceAsStream("temp_pex_path");
		BufferedReader reader = new BufferedReader(new InputStreamReader(in));
		String line = reader.readLine();
		reader.close();
		*/
		File file = new File(line3+line+"pex-slice.xml");//Dobbiamo definire bene la cartella dove collocare il file. Dovrebbe essere /Run
		FileWriter fw = new FileWriter(file, false);
		
		
		fw.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
		fw.write("<pex-slice xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"pex-slice.xsd\">\n");
		fw.write("<horizontal pex_id=\""+tempID+"\" priority=\""+priority+"\">\n");
		
			
			for(RuleDefinitionClass defxml:rule_list){
			
				
				//ethernet_src ethernet_dst ip_src ip_dst tcp_src tcp_dst udp_src udp_dst
			fw.write("<rule direction=\""+defxml.getDirection()+"\" ");
			if(!defxml.getIpD().equals("*")){
				fw.write("ip_dst=\""+defxml.getIpD()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("ip_src=\""+defxml.getIpS()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("ethernet_src=\""+defxml.getMacS()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("ethernet_dst=\""+defxml.getMacD()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("tcp_src=\""+defxml.getTcpSP()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("tcp_dst=\""+defxml.getTcpDP()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("udp_src=\""+defxml.getUdpSP()+"\" ");
			}
			if(!defxml.getIpS().equals("*")){
				fw.write("udp_dst=\""+defxml.getUdpDP()+"\" ");
			}
			
			fw.write("/>\n");
			
			}
			fw.write("</horizontal>\n");
		
		//<rule direction="IN" ip_src="1.1.1.1" tcp_src="80"/>
		fw.write("</pex-slice>");
		fw.flush();
		
		
		fw.close();
		
		
		nodes = doc.getElementsByTagName("script_path");
		node = nodes.item(0);
		element = (Element) node;
		nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		node2 = (Node) nodes2.item(0);
		String line2=node2.getNodeValue();
		/*
		InputStream in2 = getClass().getClassLoader().getResourceAsStream("script_path");
		BufferedReader reader2 = new BufferedReader(new InputStreamReader(in2));
		String line2 = reader2.readLine();
		reader2.close();
		*/
		System.out.println(line2);
		Runtime.getRuntime().exec("bash "+line3+line2+"startPEX.sh " + "NomeApp " + tempID );
		
		/*String string_out=new String();
		string_out+="{";
		
		string_out+="\"command\" : \"new_slice\",";
		string_out+="\"pex\" : \""+tempID+"\",";
		string_out+="\"priority\" : \""+priority+"\",";
		
		string_out+="\"rules\" : [  ";
		
		int cont=0, cont2=0;
		cont=rule_list.length;
		for(RuleDefinitionClass rdc: rule_list){//
			cont2++;
			string_out+="{";
			string_out+="\"direction\" : \""+rdc.getDirection()+"\",";
		
		if(!rdc.getMacS().equals("*")){
				if(!rdc.getMacD().equals("*")||!rdc.getIpS().equals("*")||!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"eth_src\" : \""+rdc.getMacS()+"\",";
				}else{
					string_out+="\"eth_src\" : \""+rdc.getMacS()+"\"";
				}
			}
			if(!rdc.getMacD().equals("*")){
				if(!rdc.getIpS().equals("*")||!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"eth_dst\" : \""+rdc.getMacD()+"\",";
				}else{
					string_out+="\"eth_dst\" : \""+rdc.getMacD()+"\"";
				}
			}
			if(!rdc.getIpS().equals("*")){
				if(!rdc.getIpD().equals("*")||!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"ip_src\" : \""+rdc.getIpS()+"\",";
				}else{
					string_out+="\"ip_src\" : \""+rdc.getIpS()+"\"";
				}
			}
			if(!rdc.getIpD().equals("*")){
				if(!rdc.getTcpSP().equals("*")||!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"ip_dst\" : \""+rdc.getIpD()+"\",";
				}else{
					string_out+="\"ip_dst\" : \""+rdc.getIpD()+"\"";
				}
			}
			if(!rdc.getTcpSP().equals("*")){
				if(!rdc.getTcpDP().equals("*")||!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"tcp_src\" : \""+rdc.getTcpSP()+"\",";
				}else{
					string_out+="\"tcp_src\" : \""+rdc.getTcpSP()+"\"";
				}
			}
			if(!rdc.getTcpDP().equals("*")){
				if(!rdc.getUdpSP().equals("*")||!rdc.getUdpDP().equals("*")){
				string_out+="\"tcp_dst\" : \""+rdc.getTcpDP()+"\",";
				}else{
					string_out+="\"tcp_dst\" : \""+rdc.getTcpDP()+"\"";
				}
			}
			if(!rdc.getUdpSP().equals("*")){
				if(!rdc.getUdpDP().equals("*")){
				string_out+="\"udp_src\" : \""+rdc.getUdpSP()+"\",";
				}else{
					string_out+="\"udp_src\" : \""+rdc.getUdpSP()+"\"";
				}
			}
			if(!rdc.getUdpDP().equals("*")){
				string_out+="\"udp_dst\" : \""+rdc.getUdpDP()+"\"";
			}
			
			
			if(cont!=cont2){
			string_out+="},";
			}else{
				string_out+="}";
			}
		}
		string_out+="],";
		string_out+="\"type\" : \"horizontal\"";
		
		
		string_out+="}";
		
		System.out.println(string_out);
		*/
		
		/*
	try{	
		int sent=0;
		File file = new File("HSdump.txt");///home/gianmarco/
		FileWriter fw = new FileWriter(file, true);
		fw.close();

		String line;
		File tempFile= new File(file.getAbsolutePath()+".tmp");
		FileWriter tw = new FileWriter(tempFile, true);
		BufferedReader br = new BufferedReader(new FileReader(file));
		
		while((line= br.readLine())!=null){
			System.out.println("LA LINEA ANALIZZATA="+line);
			if((line.contains("\"priority\" : \""+priority+"\""))){
				System.out.println("trovato pex");
				
				if(line.contains("timestamp="+timestamp)){
				sent=1;
				tw.write(line+"\n");
				tw.flush();
				}else{
					sent=0;
				}
			}else{
				tw.write(line+"\n");
				tw.flush();
				
			}
		}
		tw.close();
		br.close();
	
		
		
		
		if(file.delete())
			System.out.println("File eliminato");

		if(sent!=1){
		FileWriter fws = new FileWriter(tempFile, true);
		
		fws.write(string_out+" timestamp="+timestamp+"\n");
		fws.flush();
		fws.close();
		}
		
		if(tempFile.renameTo(file))
			System.out.println("File rinominato");

	}catch(FileNotFoundException e){
		System.out.println("File not found");
	}catch(IOException e){
		System.out.println("IOException");
	}
	*/
	
	
	
		/*Socket so=new Socket("127.0.0.1", 2525);
		DataOutputStream os= new DataOutputStream(so.getOutputStream());
		
		os.write(string_out.getBytes(Charset.forName("UTF-8")));
		
		
		
		
		os.close();
		
		so.close();*/
		
		
		out.print("true");
		
		System.out.println("Stiamo ricevendo i dati:");
		
		//}else{
			//System.out.println("Slice gia' aggiornata");
			//out.print("false");
		//}
		System.out.println("INFO: ...servlet_PullDB executed.");
		}
		

}
