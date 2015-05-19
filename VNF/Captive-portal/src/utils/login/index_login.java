package utils.login;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.net.ProtocolException;
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

import com.google.gson.Gson;

import log.impl.WebLogger;



@WebServlet("/servlet_login")
public class index_login extends HttpServlet {
	private static final long serialVersionUID = 1L;
	public static Hashtable<Integer, HashTabValue> table2= new Hashtable<Integer, HashTabValue>();
	//public static Hashtable<Integer, HashTabValue> tableHS= new Hashtable<Integer, HashTabValue>();
	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public index_login() {
		super();
			}

	
	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "rawtypes", "unchecked" })
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		WebLogger.getInstance().getLog().info("Request to login");
		System.out.println("INFO: Executing servlet_login...");
		//Session s=(Session) request.getAttribute("Session");
		
		String Ipaddr_local = request.getLocalAddr();			//address of tap0
		
		System.out.println("DEBUG: Local Ip address = " + Ipaddr_local);
		
		String Ipaddr_remote = request.getRemoteAddr();			//addess assigned to user
		
		System.out.println("DEBUG: Remote Ip address = " + Ipaddr_remote);
		
		//String salt=(String) request.getAttribute("salt");
		//Date lastSeen=new Date();
		PrintWriter out = response.getWriter();
		String username=request.getParameter("username");
		String pwd=request.getParameter("password");
		String ip=request.getRemoteAddr();

		String success="";
		String MacValue=null;
							
					
					//richiesta al server per user + pass 
					//if pass o user errati return false
					//if user e pass ok return true
	/////////////////////////////////////////////////////////////				

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
	
		try
		{
			String temp="";
			String s_url=mgmt_addr+"/LoginClientRouter";
			System.out.println("[DEBUG] URL contacted: "+ s_url);
					
			temp+="username="+username+"&password="+pwd;
			URL url = new URL(s_url+"?"+temp);

			System.out.println("[DEBUG] Contacting this URL: " + s_url + "?" + temp);
	
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
				
			connection.setConnectTimeout(15000);
			connection.setReadTimeout(15000);
		    connection.setRequestMethod("GET");

			
			connection.connect();
					
			int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
			System.out.println("[DEBUG] Return code: " + status);
//			connection.connect();
				
			BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
					
			String resp;
					
			while((resp=read.readLine())!=null)
			{	
				success=new Gson().fromJson(resp,String.class);
				System.out.println("[DEBUG] Server response. Servlet /LoginClientRouter:"+success);	
			}
					
			read.close();
		}
		
//		catch(MalformedURLException e)
//		{
//			System.out.println("[DEBUG] Login error");
//			e.printStackTrace();
//		}
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

		//success="true";
		if(success.equals("true"))
		{
					
///////////////////////////////////////////////////////////////////////////////
					
					
				System.out.println("[DEBUG] password:"+pwd);
					//System.out.println(user.getPassword().toString());
					
						request.getSession().setAttribute("user", username);
						//request.getSession().setAttribute("port", 9100);//(ip.substring(ip.lastIndexOf(".")+1, ip.length())));
						Cookie cookie1 = new Cookie("user",  username);
						cookie1.setMaxAge(30*60);
						cookie1.setPath("/");
						response.addCookie(cookie1); 

			
				System.out.println("Index_login");

				

				//<--------------------------------------Parte connessione con DHCP
				String string_out2=new String();
				string_out2+="GET who is "+ip+"\r\n";
				
				try{
					Socket so=new Socket("127.0.0.1", 9876);
					DataOutputStream os= new DataOutputStream(so.getOutputStream());
					BufferedReader is = new BufferedReader(new InputStreamReader(so.getInputStream()));
					
					os.writeBytes(string_out2);
					
					String responseline=null;
					while ((responseline=is.readLine())!=null){
						MacValue=responseline;
						System.out.println("[DEBUG] DHCP response:"+responseline);
						
					}
					System.out.println("[DEBUG] MAC after DCHP response(empty if not response):"+MacValue);
					if(MacValue==null){
						System.out.println("[DEBUG] Error in DHCP response: MAC address not founded");
						System.exit(1);
					}
					os.close();
					is.close();
					so.close();
				
				}catch(UnknownHostException e){
					System.out.println("Host unknown");
				}catch(IOException e){
					System.out.println("[DEBUG] Error: DHCP not response: stopping LocalServer");
					System.exit(1);					
				}
				
				int back=0;
				ServletContext context = getServletContext();
				Hashtable<Integer, HashTabValue> idPex=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab2");
				if(idPex!=null && table2.isEmpty()){
					table2=idPex;
				}
				Map<Integer,HashTabValue> sortedMap= new TreeMap<Integer, HashTabValue>(table2);
				
				Set s1=sortedMap.entrySet();
				Iterator it1=s1.iterator();
				
				while(it1.hasNext()){
					
					
					Map.Entry m1=(Map.Entry)it1.next();
					HashTabValue mm1=new HashTabValue();
					
					mm1=(HashTabValue)m1.getValue();
					if(mm1.getValue2().equals(MacValue)){
						back=1;
						System.out.println("MAC Found");
					
				}
					
				}
				
				
			
				if(back==0){
			
				//System.out.println(string_out2);
				
				
						HashTabValue temp1=new HashTabValue(username, MacValue);
						int contatore=0;
						int tempID=0;
						
						
						
						if(table2.isEmpty()){
							tempID=1;
							table2.put(tempID, temp1);//MAC no username here
							System.out.println("[DEBUG] Hashmap vuota");
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
						
						
						Set ss=table2.entrySet();
						Iterator it=ss.iterator();
						
						while(it.hasNext()){
							
							Map.Entry m=(Map.Entry)it.next();
							HashTabValue mm=new HashTabValue();
							
							mm=(HashTabValue)m.getValue();
							
								System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
						}
						
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
						
						//INSERT HERE SCRIPT TO CREATE DOC FOR PEX#
						/*
						InputStream in = getClass().getClassLoader().getResourceAsStream("temp_pex_path");
						BufferedReader reader = new BufferedReader(new InputStreamReader(in));
						String line = reader.readLine();
						reader.close();
						*/
						
						
						
						//start the write of xml file in pex folder
						
						String ResponseAppInst="";
						List<String> nameapp = new ArrayList<String>();
						List<String> statusapp = new ArrayList<String>();
						
						try{
							
								String AppInst="";
								String ServerURL=mgmt_addr+"/Search_User_App_Inst";			//we have to call this servlet in mgmtsever
								System.out.println("Stiamo contattando: "+ ServerURL);
								
								AppInst+="userPEX="+username;
								URL url = new URL(ServerURL+"?"+AppInst);
								System.out.println("[DEBUG] ServerURL + DATA:"+ServerURL+"?"+AppInst);
								
								HttpURLConnection connection = (HttpURLConnection) url.openConnection();
							    
								//http connect to that servlet
								
								connection.setConnectTimeout(10000);
								connection.setReadTimeout(10000);//timeoutLettura
							    connection.setRequestMethod("GET");
							    connection.connect();
							    int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
								System.out.println(status);
								
								
								BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
								
								String resp;
								
								while((resp=read.readLine())!=null){				//read the response of the servlet (the format is: nameapp1:statusapp1,nameapp2:statusapp2 ecc.)
									System.out.println(resp);
							
									String[] splits = resp.split(",");
									
									for(String s: splits){
										String[] splits2 = s.split(":");
										nameapp.add(splits2[0]);
										System.out.println("name = " + splits2[0]);
										statusapp.add(splits2[1]);
										System.out.println("status = " + splits2[1]);
									}
								}
								
								read.close();
								
							}catch(IOException e){
								System.out.println("errore IOEXception");
								
							}
						
						
						System.out.println("[DEBUG] Writing apps installed in pex-applications.xml");
						
						
						
						
						
						//writing pex-slice.xml
						
						
						File file = new File(line3+line+"pex-slice.xml");//Dobbiamo definire bene la cartella dove collocare il file. Dovrebbe essere /Run
						FileWriter fw = new FileWriter(file, false);
						
						
						fw.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
						fw.write("<pex-slice xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"pex-slice.xsd\">\n");
						fw.write("<vertical pex_id=\""+tempID+"\" mac_address=\""+MacValue.toUpperCase()+"\"/>\n");
						fw.write("</pex-slice>");
						fw.flush();
						
						
						fw.close();
						
						
						//writing pex-application.xml
						
						File file2 = new File(line3+line+"pex-applications.xml");//Dobbiamo definire bene la cartella dove collocare il file. Dovrebbe essere /Run
						FileWriter fw2 = new FileWriter(file2, false);
						
						
						fw2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
						fw2.write("<pex-applications xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"pex-applications.xsd\">\n");
						//fw2.write("<vertical pex_id=\""+tempID+"\" mac_address=\""+MacValue.toUpperCase()+"\"/>\n");
						fw2.write("<privileges can_modify_pkt=\"true\" can_select_interfaces=\"true\" can_drop_pkt=\"true\"/>\n");//TODO: take this value from server. Add second and third value on server first.....
						fw2.write("<applications_list>\n");
						
						
						int size = nameapp.size();
						
						//for any app installed
						for(int i=0; i<size; i++)
						{
							//write the correct status
							String running=null;
							if(statusapp.get(i).equals("0")){
								running="false";
							}
							else if(statusapp.get(i).equals("1")){
								running="true";
							}
							if(statusapp.get(i).equals("2")){
								running="false";
							}
// FULVIO 1/11/2013
// E' corretto usare la variabile Serv_p per raggiungere il server di management? Peraltro, non e' che c'e' modo di dargli un nome maggiormente significativo?
							
//ANDREA 7/11/2013 
//cambiato il nome in mgmt_addr, similarmente a quello presente nel file xml; la destinazione dovrebbe essere corretta in quanto dovrebbe far riferimento alla cartella webapps nel mgmtserver 

							
							String resp=null;
							String authorized_users = null;
							//write the users attribute of application tag: we have to contact the mgmt server
							try{
								
								String AppInst="";
								String ServerURL=mgmt_addr+"/Authorized_Users";			//we have to call this servlet in mgmtsever
								System.out.println("Stiamo contattando: "+ ServerURL);
								
								AppInst+="userPEX="+username+"&nameapp="+nameapp.get(i);
								URL url = new URL(ServerURL+"?"+AppInst);
								System.out.println("[DEBUG] ServerURL + DATA:"+ServerURL+"?"+AppInst);
								
								HttpURLConnection connection = (HttpURLConnection) url.openConnection();
							    
								//http connect to that servlet
								
								connection.setConnectTimeout(10000);
								connection.setReadTimeout(10000);//timeoutLettura
							    connection.setRequestMethod("GET");
							    connection.connect();
							    int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
								System.out.println(status);
								
								
								BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));
								
								
								
								while((resp=read.readLine())!=null){				
									System.out.println(resp);
									authorized_users=resp;
								}
								
								read.close();
								
							}catch(IOException e){
								System.out.println("errore IOEXception");
								
							}
							
							
							
							fw2.write("<application name=\"" + mgmt_addr + "/applications/"+ nameapp.get(i) +".jar\" was_started=\""+running+"\" users=\""+authorized_users+"\" />\n");

//	FULVIO 1/11/2013 I had to comment this line. The 'status' attribute is not allowed in the xsd, hence
//	the pex fails to start. So, either you modify the xsd, or you get rid of this info (btw, what is 'status' for?)
//	(I replaced with the attribute 'was_started', which was actually defined in the XSD)
//	fw2.write("<application name= \""+ nameapp.get(i) +"\" status= \""+ statusapp.get(i) +"\">\n");
							
//ANDREA 7/11/2013 
//the attribute 'was_started' is correct, but i think that his value can be change and isn't always = true 
//ANDREA 8/11/2013 ==> tested it: only if the value is true the app start in the PEX. I have always doubts on the DEFAULT possible value.
						}

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
						
					
						System.out.println("[DEBUG] Executing command: " + "bash "+line3+line2+"startPEX.sh " + tempID);
						Runtime.getRuntime().exec("bash "+line3+line2+"startPEX.sh " + tempID );
						//System.out.println("PEX started at ip: " +ip+" "+ "  ");
						
						
						String ResponseRoutValue="";
						
						try
						{
							
							String RoutVal="";
							String ServerURL=mgmt_addr+"/RouterValue";

							int portaPEX=10000+tempID;

							RoutVal+="IDPEX="+tempID+"&portaPEX="+portaPEX+"&userPEX="+username+"&addrFROG="+Ipaddr_local;

							URL url = new URL(ServerURL+"?"+RoutVal);

							System.out.println("[DEBUG] Contacting this URL: "+ServerURL+"?"+RoutVal);
							
							HttpURLConnection connection = (HttpURLConnection) url.openConnection();

//							System.out.println("[DEBUG] Contacting this URL (step2)");

							// Increasing the timeout to 15 seconds, as sometimes the answer from the server is rather slow.
							connection.setConnectTimeout(15000);
							connection.setReadTimeout(15000);
//							System.out.println("[DEBUG] Contacting this URL (step3)");
						    connection.setRequestMethod("GET");
//							System.out.println("[DEBUG] Contacting this URL (step4)");

							
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
						
						
						
						//creat directory if doesn't exist
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
							if (e.getAttribute("MAC").equals(MacValue) && e.getAttribute("user").equals(username)) {
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
							newChild.setAttribute("user", username);
							newChild.setAttribute("MAC", MacValue);
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
												
						out.print("{success,true,"+localserver_addr+"}");
						out.flush();
						System.out.println("Login done.");
					}else{
						out.print("{success,error}");
						out.flush();
						System.out.println("Login is not done. An error is occured");
					}
	}else{
		out.print("{success,false}");
		out.flush();
		System.out.println("Login is not done. User or Pass wrong");
		
	}

	}
	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
