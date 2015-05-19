package timer;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.net.URLConnection;
import java.util.TimerTask;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
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

public class CheckMgmt extends TimerTask{

	@Override
	public void run() {
		
		
		//the first part of this servlet (Chekmgmt) try to contact the mgmt server to know if it is enabled
		System.out.println("INFO: Executing servlet_CheckMgmt...");
		
		/* ANDREA some times at this point the localserver return an exception (i don't known the meaning) but it doesn't crash. the exception is this:
		  
		Error:
		INFO: Illegal access: this web application instance has been stopped already. Could not load com.sun.org.apache.xerces.internal.impl.dv.dtd.DTDDVFactoryImpl. 
		The eventual following stack trace is caused by an error thrown for debugging purposes as well as to attempt to terminate the thread which caused the illegal access, and has no functional impact.
		java.lang.IllegalStateException
		  
		 */
		
		
		int flag = 0; //used to check if mgmmt server is enabled
		
		//search and read the file xml
		File fileXML = new File(System.getProperty("catalina.base")+"/webapps/ROOT/WEB-INF/classes/FrogRelativePath.xml");
		DocumentBuilderFactory dbFactory1 = DocumentBuilderFactory.newInstance();
		DocumentBuilder dBuilder1;
		Document doc=null;
		try {
			dBuilder1 = dbFactory1.newDocumentBuilder();
			doc = dBuilder1.parse(fileXML);
		} catch (ParserConfigurationException e1) {
			e1.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		doc.getDocumentElement().normalize();			
		
		//read the relative path with mgmt address
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
		
		
		//read the relative path with local address
		NodeList nodes1 = doc.getElementsByTagName("localserver_address");
		Node node1 = nodes1.item(0);
		Element element1 = (Element) node1;
		NodeList nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
		Node node3 = (Node) nodes3.item(0);	
		
		String url1 = node3.getNodeValue();
		
		String addr = null;
		
		try{
			addr = url1.split("//")[1];
		}
		catch(Exception e){
			addr=url1;
		}
		
		System.out.println("[DEBUG] localserver address = "+ addr);		
		String port = null;
		String ip = null;
		
		try{					
			ip =  addr.split(":")[0];				
			port = addr.split(":")[1];		
		}
		catch(Exception e){
			ip = addr;
			port="80";
		}
						
		try
		{
			//contact the management server to know if it is reachable
			String s_url=mgmt_addr+"/CheckMgmtAlive?ipaddr="+ip+"&port="+port;
			System.out.println("[DEBUG] URL contacted: "+ s_url);			
			
			URL url = new URL(s_url);
			
			//http connection
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
		      	    
			connection.setConnectTimeout(15000);//timeout
			connection.setReadTimeout(15000);
		    connection.setRequestMethod("GET");
		    connection.connect();
		    
		    //get the response
			int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
			System.out.println(status);
			
			//if the response is OK
			if(status == HttpURLConnection.HTTP_OK){
				System.out.println("INFO: management server is enable");	
				flag=1;
			}
			else{
				System.out.println("INFO: management server is not enable");
			}	
		}
		catch(ProtocolException e)
		{
			System.out.println("INFO: management server is not enable");
			e.printStackTrace();
		}
		catch(IOException e)
		{
			System.out.println("INFO: management server is not enable");
			e.printStackTrace();
		}
		System.out.println("INFO: ....servlet_CheckMgmt Executed");
		
		
		
		//the second part of this servlet (CheckAlive) try to cantact all the pex associated to this localserver: close them if htey are not enabled
		//this part is executed only if flag is equal to 1
		
		if(flag==1)
		{
			System.out.println("INFO: Executing servlet_CheckAlive...");
	
			String line = null;
			
			try{
				URL url = new URL(mgmt_addr+"/Search_Port_PEX_Alive?ipaddr="+ip);
	
				System.out.println("[DEBUG] URL contacted: "+ url.toString());
				
				
	
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
				
				//read the response of the servlet (the format is: port1,port2,port3 ecc.)
				while((resp=read.readLine())!=null){				
					line = resp;
					System.out.println("[DEBUG] Search_Port_PEX_Alive: Response from MgmtServer "+line);
					
				}
				read.close();
	
			
			}catch (MalformedURLException e)
			{
				System.out.println("Malformed exception");
				e.printStackTrace();
			}catch (IOException e){
				System.out.println("IO exception");
				e.printStackTrace();
			}
			
			//if there is at least one pex associated
			if(line!=null){
				
				String[] splits = line.split(",");
				
				//for any pex
				for(String port1 : splits){
					
					System.out.println("INFO: PEX at port "+ port1);
					
					try{
						
						//contact it to this url (response true if they are enabled)
						URL url = new URL("http://127.0.0.1:"+port1+"/hello");
						System.out.println("[DEBUG] Contacting "+ url.toString());
						HttpURLConnection connection = (HttpURLConnection) url.openConnection();
					    
						//http connect to that servlet
						
						connection.setConnectTimeout(10000);
						connection.setReadTimeout(10000);//timeoutLettura
					    connection.setRequestMethod("GET");
					    connection.connect();
					    int status=connection.getResponseCode();//STATUS connession .----> status != httpURLConnection.HTTP_OK
						System.out.println(status);
						
						//if the status is HTTP_OK the pex is enabled
						if(status == HttpURLConnection.HTTP_OK){
							System.out.println("INFO: PEX at port "+ port1 +" is enable");			
						}				
						
					}catch(IOException io){
						
						//if it isn't enabled
						System.out.println("INFO: PEX at port "+ port1 +" is not enable: remove it from mgmtserver");
						
						//contact the mgmt server at this url that remove the pex from table VerticalPEXList
						try{
							URL url = new URL(mgmt_addr+"/Delete_PEX_at_port?ipaddr="+ip+"&port="+port1);
	
							System.out.println("[DEBUG] URL contacted: "+ url.toString());
							
							
	
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
							String idpex=null;
							
							//read the response of the servlet (it contains the id of the pex that we are removing)
							while((resp=read.readLine())!=null){				
								idpex = resp;
								System.out.println("[DEBUG] Delete_PEX_at_port: Response from MgmtServer -> pex folder to delete is PEX"+idpex);
								
							}	
							read.close();
							
							//if the pex exists we have to remove his folder from file system
							if(idpex!=null){
								
								//read the relative path with absolute_path_frogs
								nodes = doc.getElementsByTagName("absolute_path_frog");
								node = nodes.item(0);
								element = (Element) node;
								nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
								node2 = (Node) nodes2.item(0);
											
								String absolute_path_frog = node2.getNodeValue();
								
								
								//read the relative path with running pex folder
								nodes1 = doc.getElementsByTagName("temp_pex_path");
								node1 = nodes1.item(0);
								element1 = (Element) node1;
								nodes3 = element1.getElementsByTagName("url").item(0).getChildNodes();
								node3 = (Node) nodes3.item(0);	
								
								String temp_pex_path = node3.getNodeValue();
								
								//delete the pex folder from file system
								System.out.println("[DEBUG] Deleting folder PEX"+idpex);
								
								String command = "sudo rm -rf "+absolute_path_frog+temp_pex_path+"pex" + idpex;
								
								System.out.println("[DEBUG] command to run = "+command);
								
								Runtime.getRuntime().exec(command);
								
								System.out.println("[DEBUG] Folder PEX"+idpex+ " deleted");
							}
							
							//also we have to remove from ActivePEX.xml the line relative to this pex
							System.out.println("[DEBUG] Removing PEX"+idpex+ " from ActivePEX.xml");
							
							//read the path for this xml file
							NodeList nodes5 = doc.getElementsByTagName("active_pex_configfile");
							Node node5 = nodes5.item(0);
							Element element2 = (Element) node5;
							NodeList nodes4 = element2.getElementsByTagName("url").item(0).getChildNodes();
							Node node4 = (Node) nodes4.item(0);
							String line4=node4.getNodeValue();
							
							//find the file
							fileXML = new File(System.getProperty("catalina.base")+"/"+line4+"ActivePex.xml");
							
							//read the file
							DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
							DocumentBuilder dBuilder;
							Document doc1=null;
							try {
								dBuilder = dbFactory.newDocumentBuilder();
								doc1 = dBuilder.parse(fileXML);
							} catch (ParserConfigurationException e1) {
								e1.printStackTrace();
							} catch (SAXException e) {
								e.printStackTrace();
							}
							doc1.getDocumentElement().normalize();
							
							//if there is one line relative to pex id that we want remove, delete it
							nodes1 = doc1.getElementsByTagName("PEX");
							for (int i=0 ; i< nodes1.getLength(); i++){
								Element e = (Element) nodes1.item(i);
								if (e.getAttribute("PEXID").equals(idpex)) {
									System.out.println ("username finded = "+e.getAttribute("user"));								
									nodes2 = doc1.getElementsByTagName("ActivePEX");
									Element e1 = (Element) nodes2.item(i);
									e1.removeChild(nodes1.item(i));
									System.out.println("[DEBUG] PEX"+idpex+ " removed from ActivePEX.xml");
								}
							}
							
							
							//write the new xml file
							PrintStream stream=new PrintStream(fileXML);
							TransformerFactory xformFactory = TransformerFactory.newInstance ();
							Transformer idTransform;
							try {
								idTransform = xformFactory.newTransformer ();
								//idTransform.setOutputProperty(OutputKeys.DOCTYPE_SYSTEM,"access.dtd");
								idTransform.setOutputProperty(OutputKeys.INDENT, "yes");
								Source input = new DOMSource (doc1);
								StreamResult output = new StreamResult (stream);
								idTransform.transform (input, output);
							} catch (TransformerConfigurationException e) {
								// TODO Auto-generated catch block
								e.printStackTrace();
							} catch (TransformerException e) {
								// TODO Auto-generated catch block
								e.printStackTrace();
							}
							
							
							
							
							
						}catch (MalformedURLException e)
						{
							System.out.println("Malformed exception");
							e.printStackTrace();
						}catch (IOException e){
							System.out.println("IO exception");
							e.printStackTrace();
						}	
											
					}
					
				}
				
				
			}
			System.out.println("INFO: ....servlet_CheckAlive Executed");

		}	

	}
}
