package utils.admin;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.ProtocolException;
import java.net.Socket;
import java.net.URL;
import java.net.UnknownHostException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Result;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import utils.login.HashTabValue;
import utils.login.index_login;

import com.google.gson.Gson;

import log.impl.WebLogger;

@WebServlet("/create_empty_pex")
public class CreateEmptyPex extends HttpServlet {
	/**
	 * 
	 */
	private static final long serialVersionUID = 4586579284435807495L;

	private static Hashtable<Integer, HashTabValue> table2= index_login.table2;

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "rawtypes", "unchecked" })
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		WebLogger.getInstance().getLog().info("Request to create_empty_pex");
		System.out.println("INFO: Executing create_empty_pex...");
		
		String Ipaddr_local = request.getLocalAddr();			//address of tap0		
		System.out.println("DEBUG: Local Ip address = " + Ipaddr_local);		
		String Ipaddr_remote = request.getRemoteAddr();			//addess assigned to user		
		System.out.println("DEBUG: Remote Ip address = " + Ipaddr_remote);
		
		String user=request.getParameter("user");
		String macaddr=request.getParameter("macaddr");
		
		PrintWriter out = response.getWriter();

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

		NodeList nodes = doc.getElementsByTagName("mgmtserver_address");
		Node node = nodes.item(0);
		Element element = (Element) node;
		NodeList nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		Node node2 = (Node) nodes2.item(0);
		
		String mgmt_addr1 = node2.getNodeValue();
		String mgmt_addr=null;
		
		if(mgmt_addr1.contains("http://")){
			mgmt_addr=mgmt_addr1;
		}
		else{
			mgmt_addr="http://"+mgmt_addr1;
		}
		
		nodes = doc.getElementsByTagName("localserver_address");
		node = nodes.item(0);
		element = (Element) node;
		nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		node2 = (Node) nodes2.item(0);
		String url1 = node2.getNodeValue();
		
		String localserver_addr = null;
		
		if(url1.contains("http://")){
			localserver_addr=url1;
		}
		else{
			localserver_addr="http://"+url1;
		}
		
		HashTabValue temp1=new HashTabValue(user, macaddr);
		int contatore=0;
		int tempID=0;
		
		if(table2.isEmpty()){
			tempID=1;
			table2.put(tempID, temp1);//MAC no username here
			System.out.println("[DEBUG] Hashmap vuota");
		}else{
			Map<Integer,HashTabValue> sortedMap= new TreeMap<Integer, HashTabValue>(table2);
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			tempID++;
			while(it.hasNext()){
				tempID++;
				contatore++;
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				
				
				if(!m.getKey().equals(contatore)){
					System.out.println("[DEBUG] Dentro if chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				tempID=contatore;
				break;
			}
				
				
				mm=(HashTabValue)m.getValue();
				System.out.println("[DEBUG] chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			//System.out.println("TempID: "+tempID+" contatore"+contatore);
			table2.put(tempID, temp1);
			
		}//End else
		
		this.getServletContext().setAttribute("HashTab", table2);
		//this.getServletContext().setAttribute("HashTabHS", tableHS);
		
		
		NodeList nodes1 = doc.getElementsByTagName("absolute_path_frog");
		Node node1 = nodes1.item(0);
		Element element1 = (Element) node1;
		NodeList nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
		Node node3 = (Node) nodes3.item(0);
		String line3=node3.getNodeValue();
		
		nodes = doc.getElementsByTagName("temp_pex_path");
		node = nodes.item(0);
		element = (Element) node;
		nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
		node2 = (Node) nodes2.item(0);
		String line=node2.getNodeValue();
						
						
		//start the write of xml file in pex folder
						
		String ResponseAppInst="";
		List<String> nameapp = new ArrayList<String>();
		List<String> statusapp = new ArrayList<String>();
						
		
		// No apps need to be installed! :D
		
		try{
			System.out.println("[DEBUG] Writing "+ line3+line+"pex-slice.xml");
						
			//writing pex-slice.xml
			
			File file = new File(line3+line+"pex-slice.xml");//Dobbiamo definire bene la cartella dove collocare il file. Dovrebbe essere /Run
			FileWriter fw = new FileWriter(file, false);
			
			fw.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
			fw.write("<pex-slice xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"pex-slice.xsd\">\n");
			fw.write("<vertical pex_id=\""+tempID+"\" mac_address=\""+macaddr.toUpperCase()+"\"/>\n");
			fw.write("</pex-slice>");
			fw.flush();
						
			fw.close();
						
						
			//writing pex-application.xml
			System.out.println("[DEBUG] Writing "+ line3+line+"pex-applications.xml");
						
			File file2 = new File(line3+line+"pex-applications.xml");//Dobbiamo definire bene la cartella dove collocare il file. Dovrebbe essere /Run
			FileWriter fw2 = new FileWriter(file2, false);
			
			fw2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
			fw2.write("<pex-applications xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"pex-applications.xsd\">\n");
			fw2.write("<privileges can_modify_pkt=\"true\" can_select_interfaces=\"true\" can_drop_pkt=\"true\"/>\n");//TODO: take this value from server. Add second and third value on server first.....
			fw2.write("<applications_list>\n");
			
			//no apps needed. whoo!
			
			fw2.write("</applications_list>\n");
			fw2.write("</pex-applications>\n");
			fw2.flush();

			fw2.close();
						
			nodes = doc.getElementsByTagName("script_path");
			node = nodes.item(0);
			element = (Element) node;
			nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
			node2 = (Node) nodes2.item(0);
			String line2=node2.getNodeValue();
			
			System.out.println("[DEBUG] Executing command: " + "bash "+line3+line2+"startPEXlight.sh " + tempID);
			Runtime.getRuntime().exec("bash "+line3+line2+"startPEXlight.sh " + tempID );
						
			String ResponseRoutValue="";
						
			int portaPEX=10000+tempID;
			
			try
			{
							
				String RoutVal="";
				String ServerURL=mgmt_addr+"/RouterValue";

				RoutVal+="IDPEX="+tempID+"&portaPEX="+portaPEX+"&userPEX="+user+"&addrFROG="+Ipaddr_local;

				URL url = new URL(ServerURL+"?"+RoutVal);

				System.out.println("[DEBUG] Contacting this URL: "+ServerURL+"?"+RoutVal);
				
				HttpURLConnection connection = (HttpURLConnection) url.openConnection();

				// Increasing the timeout to 15 seconds, as sometimes the answer from the server is rather slow.
				connection.setConnectTimeout(15000);
				connection.setReadTimeout(15000);
			    connection.setRequestMethod("GET");
				
				connection.connect();

				int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
//							System.out.println("[DEBUG] Contacting this URL (step5)");
				System.out.println("[DEBUG] Return code: " + status);
				
//							connection.connect();
				
				BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
				
				String resp;
				
				while((resp=read.readLine())!=null)
				{
					//System.out.println(resp);
					ResponseRoutValue=new Gson().fromJson(resp,String.class);
					System.out.println("[DEBUG] Response from server. Servlet /RouterValue:"+ResponseRoutValue);
				}

				read.close();			
			}
//						catch(MalformedURLException e)
//						{
//							System.out.println("[DEBUG] Login error");
//							e.printStackTrace();
//						}
			catch(ProtocolException e)
			{
				System.out.println("[DEBUG] Login error");
				e.printStackTrace();
			}
			catch(IOException e)
			{
				System.out.println("[DEBUG] Login error");
				e.printStackTrace();
			}
			
			///////////////////////////////////////////////////////////////////////////////	
			//<-------------------------------------- Starting to write ActivePEX.xml (it contains all active pex at the moment)					

			nodes = doc.getElementsByTagName("active_pex_configfile");
			node = nodes.item(0);
			element = (Element) node;
			nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
			node2 = (Node) nodes2.item(0);
			line2=node2.getNodeValue();
						
			//create directory if doesn't exist
			Files.createDirectories(Paths.get(System.getProperty("catalina.base")+"/"+line2));
					
			System.out.println("[DEBUG] searching the file: "+ System.getProperty("catalina.base")+"/"+line2+"ActivePex.xml");
						
			fileXML = new File(System.getProperty("catalina.base")+"/"+line2+"ActivePex.xml");
						
			//if file doesn't exist, create it
			if (!fileXML.exists()){
				
				System.out.println("[DEBUG] the file "+ System.getProperty("catalina.base")+"/"+line2+"ActivePex.xml" +" doesn't exist");
				fileXML = new File(System.getProperty("catalina.base")+"/"+line2+"ActivePex.xml");
				FileWriter fw1 = new FileWriter(fileXML, false);
				
				
				fw1.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
				fw1.write("<ActivePEX>\n");
				fw1.write("</ActivePEX>\n");
				fw1.flush();
				
				fw1.close();
			}
						
			//find the file
			fileXML = new File(System.getProperty("catalina.base")+"/"+line2+"ActivePex.xml");
			dbFactory = DocumentBuilderFactory.newInstance();
			doc=null;
			try {
				dBuilder = dbFactory.newDocumentBuilder();
				doc = dBuilder.parse(fileXML);
			} catch (ParserConfigurationException e1) {
				e1.printStackTrace();
			} catch (SAXException e) {
				e.printStackTrace();
			}
						
			//read the file in a document
			doc.getDocumentElement().normalize();
			
			//set the pexID
			Integer PEXnumber = tempID;	
			
			int trovato=0;
			
			//search if this line MAC:idPEX:username is already present. If it is right, don't insert the new line into xml file
			nodes1 = doc.getElementsByTagName("PEX");
			for (int i=0 ; i< nodes1.getLength(); i++){
				Element e = (Element) nodes1.item(i);
				if (e.getAttribute("MAC").equals(macaddr) && e.getAttribute("user").equals(user)) {
					System.out.println ("[DEBUG] user "+e.getAttribute("user") + " is already in the xml. Probably it was not closed right, and not yet deleted from the file");
					trovato = 1;
				}
			}
						
			if(trovato==0)
			{
				//search the root
				nodes1 = doc.getElementsByTagName("ActivePEX");
				node1 = nodes1.item(0);
				element1 = (Element) node1;
				
				//create a new element for a new pex
				Element newChild = doc.createElement("PEX");
				newChild.setAttribute("user", user);
				newChild.setAttribute("MAC", macaddr);
				newChild.setAttribute("PEXID", PEXnumber.toString());
				
				//append the element
				element1.appendChild(newChild);
				
				
				//write the file xml
				PrintStream stream=new PrintStream(fileXML);
				TransformerFactory xformFactory = TransformerFactory.newInstance ();
				Transformer idTransform;
				try {
					idTransform = xformFactory.newTransformer ();
					//idTransform.setOutputProperty(OutputKeys.DOCTYPE_SYSTEM,"access.dtd");
					idTransform.setOutputProperty(OutputKeys.INDENT, "yes");
					Source input = new DOMSource (doc);
					Result output = new StreamResult (stream);
					idTransform.transform (input, output);
				} catch (TransformerConfigurationException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (TransformerException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
						
			System.out.println("[DEBUG] localserver address = " + localserver_addr);
						
			//we return the localserver address in the response because the page from which we have logged isn't localserver_address/login.htm but is 
			//redirect_page/login.htm (where redirect_page is the page where you are redirect before login).
									
			//out.print("{success,true,"+localserver_addr+"}");
			
			final CreatePexResponse cpr = new CreatePexResponse();
			cpr.address = localserver_addr + ":" + portaPEX;
			cpr.success = true;
			cpr.ID = tempID;
			
			Gson gson = new Gson();
			out.print(gson.toJson(cpr));
			//out.print("{\"success\":true, \"address\":\"" + localserver_addr + ":" + portaPEX + "\", \"id\": \"" + tempID + "\"}" );
			out.flush();
			System.out.println("Creation done.");
		} catch (ClassCastException fnfe) {
			
		}
	}
}
