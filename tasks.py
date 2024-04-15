from robocorp.tasks import task
from robocorp import browser
from robocorp import vault
from RPA.HTTP import HTTP
from RPA.Tables import Tables


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
        http = HTTP()
        http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

        orders = Tables().read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])

        return orders
    
    def close_annoying_modal():
        page = browser.page()
        page.click("text=OK")

    def fill_the_form(orderNumber,head,body,legs,address):
        print(orderNumber,head,body,legs,address)
        page = browser.page()
        page.select_option("#head",head)
        page.set_checked("input#id-body-"+str(body),True)
        page.fill("input:placeholder(Enter the part number for the legs)",str(legs))

        

#Call all sub-processes in sequence
    open_robot_order_website()
    orders = get_orders()
    close_annoying_modal()
    for order in orders:
        fill_the_form(order["Order number"],order["Head"],order["Body"],order["Legs"],order["Address"])