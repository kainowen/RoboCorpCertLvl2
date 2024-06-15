from robocorp.tasks import task
from robocorp import browser
from robocorp import vault
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    def open_robot_order_website():
        """Opens Selenium web browser to the given URL"""

        browser.configure(
        # Note: screenshot="only-on-failure" is actually the default.
        # If the browser_automate() function finishes with an exception it will
        # make a screenshot and embed it into the logs.
        screenshot="only-on-failure",
        
        # By default headless is False unless running in a Linux container
        # without a DISPLAY/WAYLAND_DISPLAY environment variable, but it
        # can also be manually specified.
        headless=False,
        
        # Interactions may be run in slow-motion (given in milliseconds).
        slowmo=100,
        )

        # browser.goto() may be used as a shortcut to get the current page and
        # go to some url (it may create the browser if still not created).
        browser.goto("https://robotsparebinindustries.com/#/robot-order")


    def get_orders():
        """Retrieves the input document via http request from the endpoint provided"""
        http = HTTP()
        http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

        orders = Tables().read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])

        return orders
    
    def close_annoying_modal():
        """Closes Consent pop-up on RobotSpareBin Website homepage"""
        page = browser.page()
        page.click("text=OK")

    def fill_the_form(orderNumber,head,body,legs,address):
        """Populates the order form and clicks preview, then submit"""
        
        page = browser.page()
        i = 5
        
        #Select Head option
        page.select_option("#head",head)
        #Check body option
        page.set_checked("input#id-body-"+str(body),True)
        #Fill leg input field with int
        page.fill("input.form-control",str(legs))
        #populated address field
        page.fill("input#address",str(address))
        #Clicks Preview
        page.click("button#preview")

        while(page.locator("button#order").is_visible() and i > 0):
          #Loops through clicking submit while the submit button is visable in order to overcome submit error, maxumum retries defined by i above
          page.click("button#order")
          i=i-1

        if(page.locator("button#order").is_visible()):
            #Raises an exception if the order button is still visable after i attempts at clicking submit
            raise Exception("Could not place order. Submit button failed too many times in a row.")
        
    def order_more():
        """Clicks the 'Order Another' button to return to order form"""

        #Clicks the Order Another button after retrieving reciept details
        page = browser.page()
        page.click("button#order-another")

    def store_receipt_as_pdf(order_number):
        """Saves reciept html and saves it to a pdf in the output folder"""
        #Extracts reciept table html
        page = browser.page()
        reciept_html = page.locator("#receipt").inner_html()
        
        #Defines Reciept pdf file path
        reciept_Filepath = f"output/reciepts/{order_number}_reciepts.pdf"

        #Saves html receipt to PDF at given file path
        pdf = PDF()
        pdf.html_to_pdf(reciept_html, reciept_Filepath)
        
        #Returns reciept file path
        return reciept_Filepath

    def take_Screenshot(order_number):
        """Takes Screenshot of the reciept and appends it to the Reciept pdf"""

        #Defines Target
        page = browser.page()
        locator = page.locator("#receipt")

        #Defines screenshot file path
        screenshot_path = f"output/reciepts/{order_number}_Screenshot.png"

        #Takes screenshot
        page.screenshot(path=screenshot_path)
        
        #Returns screenshot file path
        return screenshot_path
    
    def embed_screenshot_to_receipt(screenshot, pdf_file):
        """Appends the receipt screenshot to the reciept pdf"""

        #Appends target file to the pdf
        pdf = PDF()
        pdf.add_files_to_pdf(
        files = [screenshot],
        target_document = pdf_file,
        append = True
    )

    def zip_reciepts(recipts_path):
        """Creates a ZIP Archive of the recipts folder"""

        #Zips folder
        zip = Archive()
        zip.archive_folder_with_zip('output/reciepts', 'output/reciepts.zip')
        

#Call all sub-processes in sequence
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order["Order number"],order["Head"],order["Body"],order["Legs"],order["Address"])
        reciept = store_receipt_as_pdf(order["Order number"])
        screenshot = take_Screenshot(order["Order number"])
        embed_screenshot_to_receipt(screenshot,reciept)
        order_more()
    zip_reciepts("output/receipts")