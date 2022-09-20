
export class ColorManager {
    constructor(viewManager) {
        this.viewManager = viewManager;
        this.propertyColors = {}
        
        let that = this;
        this.viewManager.OnActiveProfileChanged.add(profile => {
            that.updateProfile(profile);
        });

        let initialProfile = this.viewManager.dataManager.getActiveProfile();
        if(initialProfile){
            this.updateProfile(initialProfile);
        }
    }
    
    
    getDefaultPropertyColors(numProperties) {
        let colorsLight24 = [
            "#FD3216",
            "#00FE35",
            "#6A76FC",
            "#FED4C4",
            "#FE00CE",
            "#0DF9FF",
            "#F6F926",
            "#FF9616",
            "#479B55",
            "#EEA6FB",
            "#DC587D",
            "#D626FF",
            "#6E899C",
            "#00B5F7",
            "#B68E00",
            "#C9FBE5",
            "#FF0092",
            "#22FFA7",
            "#E3EE9E",
            "#86CE00",
            "#BC7196",
            "#7E7DCD",
            "#FC6955",
            "#E48F72"
        ];

        let colors_Set3 = [
            "#8dd3c7",
            "#ffffb3",
            "#bebada",
            "#fb8072",
            "#80b1d3",
            "#fdb462",
            "#b3de69",
            "#fccde5",
            "#d9d9d9",
            "#bc80bd",
            "#ccebc5",
            "#ffed6f"
        ]; // Set3

        let colors_T10 = [
            "#4c78a8",
            "#f58518",
            "#e45756",
            "#72b7b2",
            "#54a24b",
            "#eeca3b",
            "#b279a2",
            "#ff9da6",
            "#9d755d",
            "#bab0ac"
        ]

        if(numProperties > 10){
            return colorsLight24;
        } else {
            return colors_T10;
        }
        
    }

    updateProfile(profile){        
        this.propertyColors = {}
        let defaultColorCounter = 0;        
        let defaultColors = this.getDefaultPropertyColors(profile.selection_properties.length);
        for (let i = 0; i < profile.selection_properties.length; i++) {
            let propertyMeta = profile.selection_properties[i];
            if (propertyMeta.property_type == "categorical") {
                if(propertyMeta.color !== undefined){
                    this.propertyColors[propertyMeta.name] = propertyMeta.color;
                } else {
                    let colorIdx = defaultColorCounter % defaultColors.length;
                    this.propertyColors[propertyMeta.name] = defaultColors[colorIdx]
                    defaultColorCounter += 1;
                }
            } else {
                throw Error()
            }
        }
    }

    getPropertyColor(propertyName){
        if(this.propertyColors[propertyName]){
            return this.propertyColors[propertyName]; 
        } else {
            return "grey";
        }
    }
}