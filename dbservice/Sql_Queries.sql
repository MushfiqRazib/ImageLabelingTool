CREATE TABLE public."Project_Details"
(
  "Project_Id" SERIAL,
  "Project_Name" character varying NOT NULL,
  "Date_Project" timestamptz(0) NOT NULL,
  "Parent_Project_Id" integer,
  CONSTRAINT "Project_Details_pkey" PRIMARY KEY ("Project_Id")
);

commit;


CREATE TABLE public."Image_Details"
(
    "Image_Id" uuid NOT NULL,
	"Orig_ImageName" character varying COLLATE pg_catalog."default" NOT NULL,
    "Ext_Image" character varying COLLATE pg_catalog."default" NOT NULL,
    "Dir_Image" character varying COLLATE pg_catalog."default" NOT NULL,
    "Web_Url" character varying COLLATE pg_catalog."default" NOT NULL,
    "Project_Id" integer NOT NULL,
    "Labeled" integer,
    "Critical" integer,
    "Labeling_Running" boolean,
    "Quality_Labeling" integer,
    "Is_Deleted" boolean,
    "Date_Image" timestamptz(0) NOT NULL,
    CONSTRAINT "Image_Details_pkey" PRIMARY KEY ("Image_Id"),
    CONSTRAINT "Image_Details_Project_Id_fkey" FOREIGN KEY ("Project_Id")
        REFERENCES public."Project_Details" ("Project_Id") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

Commit;

CREATE TABLE public."Label_Details"
(
    "Label_Id" SERIAL,
    "Image_Id" uuid NOT NULL,
    "Is_Deleted" boolean,
    "Label_Details" json NOT NULL,
    "Date_Label" timestamptz(0) NOT NULL,
    CONSTRAINT "Label_Details_pkey" PRIMARY KEY ("Label_Id"),
    CONSTRAINT "Label_Details_Image_Id_fkey" FOREIGN KEY ("Image_Id")
        REFERENCES public."Image_Details" ("Image_Id") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

commit;

CREATE TABLE public."Labelbox_Details"
(
  "Dataset_Id" character varying NOT NULL,
  "Dataset_Name" character varying NOT NULL,
  "Project_Id" integer,
  "LB_Project_Id" character varying NOT NULL,
  "UInterface_ID" character varying NOT NULL,
  "UInterface_Name" character varying NOT NULL,
  "Date_Labelbox" timestamptz(0) NOT NULL,
  CONSTRAINT "Labelbox_Details_pkey" PRIMARY KEY ("Dataset_Id"),
  CONSTRAINT "Labelbox_Details_Project_Id_fkey" FOREIGN KEY ("Project_Id")
      REFERENCES public."Project_Details" ("Project_Id") MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

commit;
