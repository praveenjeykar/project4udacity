from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Gun, Base, GunModel, User

engine = create_engine('sqlite:///gundatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create fake user
User1 = User(name="randy orton", email="randyrko@gmail.com",
             picture='https://bit.ly/2JOTZ8j')
session.add(User1)
session.commit()

# Arms in Patriot Ordnance Factory
guncompany1 = Gun(user_id=1, name="Patriot Ordnance Factory")

session.add(guncompany1)
session.commit()

gunModel2 = GunModel(user_id=1, name="Colt Buntline", description="The Colt Buntline Special is a long-barreled revolver",
                     price="$200", course="Revolver", guncompany=guncompany1)

session.add(gunModel2 )
session.commit()


gunModel1 = GunModel(user_id=1, name="M203 grenade launcher", description="The M203 is a single-shot 40 mm grenade launcher ",
                     price="$248.99", course="Sniper", guncompany=guncompany1)

session.add(gunModel1)
session.commit()

gunModel2 = GunModel(user_id=1, name="AAI SBR", description=" rifles in service with the United States Armed Forces ",
                     price="$521.50", course="Rifle", guncompany=guncompany1)

session.add(gunModel2)
session.commit()

gunModel3 = GunModel(user_id=1, name="AAI XM70 ", description="was chosen as an entry instead due to high production cost",
                     price="$356", course="Rifle", guncompany=guncompany1)

session.add(gunModel3)
session.commit()

gunModel4 = GunModel(user_id=1, name="Akdal Ghost TR01", description="The Ghost TR01 is a compact semi-automatic pistol ",
                     price="$723.99", course="Pistol", guncompany=guncompany1)

session.add(gunModel4)
session.commit()



# Arms in Remington Arms
guncompany2 = Gun(user_id=1, name="Remington Arms")

session.add(guncompany2)
session.commit()


gunModel1 = GunModel(user_id=1, name="ALFA Combat", description="created for sport shooting purpose",
                     price="$73.99", course="Pistol", guncompany=guncompany2)

session.add(gunModel1 )
session.commit()

gunModel2 = GunModel(user_id=1, name="ALFA Defender",
                     description="created for military ", price="$257", course="Rifle", guncompany=guncompany2)

session.add(gunModel2)
session.commit()

gunModel3 = GunModel(user_id=1, name="Series ALFA", description="series of revolvers",
                     price="$215", course="Revolver", guncompany=guncompany2)

session.add(gunModel3)
session.commit()

gunModel4 = GunModel(user_id=1, name="Series HOLEK ", description="series of pistols",
                     price="120", course="Pistol", guncompany=guncompany2)

session.add(gunModel4)
session.commit()



# Arms in Sturm, Ruger & Co. 
guncompany1 = Gun(user_id=1, name="Sturm, Ruger & Co. ")

session.add(guncompany1)
session.commit()


gunModel1 = GunModel(user_id=1, name="AutoMag", description="a short and powerful pistol",
                     price="$84.99", course="Pistol", guncompany=guncompany1)

session.add(gunModel1)
session.commit()

gunModel2 = GunModel(user_id=1, name="AMT AutoMag II", description="upgraded version of automag",
                     price="$63.99", course="Pistol", guncompany=guncompany1)

session.add(gunModel2)
session.commit()

gunModel3 = GunModel(user_id=1, name="AMT Backup", description="The AMT Backup is a small semiautomatic rifle",
                     price="$92.95", course="Rifle", guncompany=guncompany1)

session.add(gunModel3)
session.commit()




# Arms in Smith and Wesson
guncompany1 = Gun(user_id=1, name="Smith and Wesson")

session.add(guncompany1)
session.commit()


gunModel1 = GunModel(user_id=1, name="AO-31", description="The AO-31 was a Soviet fully automatic assault rifle",
                     price="$220.99", course="Rifle", guncompany=guncompany1)

session.add(gunModel1)
session.commit()

gunModel2 = GunModel(user_id=1, name="AO-35 assault rifle", description="powerful assault rifle",
                     price="$225.99", course="Rifle", guncompany=guncompany1)

session.add(gunModel2)
session.commit()

gunModel3 = GunModel(user_id=1, name="Apache revolver",
                     description="An Apache revolver is a handgun ", price="$40.50", course="Revolver", guncompany=guncompany1)

session.add(gunModel3)
session.commit()



# Arms in Beretta
guncompany1 = Gun(user_id=1, name="Beretta")

session.add(guncompany1)
session.commit()


gunModel1 = GunModel(user_id=1, name="Beretta 21A Bobcat.", description="beautiful pistol",
                     price="$90.95", course="Pistol", guncompany=guncompany1)

session.add(gunModel1)
session.commit()

gunModel2 = GunModel(user_id=1, name="Beretta 92G-SD/96G-SD.", description=" semi-automatic, locked-breech delayed recoil-operated",
                     price="$75.95", course="Rifle", guncompany=guncompany1)

session.add(gunModel2)
session.commit()

gunModel3 = GunModel(user_id=1, name="Beretta 93R.", description="The Beretta 93R is a selective-fire machine pistol",
                     price="$65.50", course="Pistol", guncompany=guncompany1)

session.add(gunModel3)
session.commit()

gunModel4 = GunModel(user_id=1, name="Beretta 950.", description="Beretta 950 is a semi-automatic pistol ",
                     price="$69.75", course="Launcher", guncompany=guncompany1)

session.add(gunModel4)
session.commit()


# Arms in Bersa
guncompany1 = Gun(user_id=1, name="Bersa")

session.add(guncompany1)
session.commit()


gunModel1 = GunModel(user_id=1, name="Bersa Thunder 22-6",
                     description="Thunder 22-6 is an unquestionable leader in sport", price="$252.95", course="Launcher", guncompany=guncompany1)

session.add(gunModel1)
session.commit()

gunModel2 = GunModel(user_id=1, name="Bersa 86", description="Designed by John Browning and introduced by Fabrique",
                     price="$127.99", course="Revolver", guncompany=guncompany1)

session.add(gunModel2)
session.commit()



print "added all arms!"
