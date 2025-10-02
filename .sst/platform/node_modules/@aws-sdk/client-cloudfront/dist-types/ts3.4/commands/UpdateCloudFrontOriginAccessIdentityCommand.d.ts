import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  UpdateCloudFrontOriginAccessIdentityRequest,
  UpdateCloudFrontOriginAccessIdentityResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateCloudFrontOriginAccessIdentityCommandInput
  extends UpdateCloudFrontOriginAccessIdentityRequest {}
export interface UpdateCloudFrontOriginAccessIdentityCommandOutput
  extends UpdateCloudFrontOriginAccessIdentityResult,
    __MetadataBearer {}
export declare class UpdateCloudFrontOriginAccessIdentityCommand extends $Command<
  UpdateCloudFrontOriginAccessIdentityCommandInput,
  UpdateCloudFrontOriginAccessIdentityCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateCloudFrontOriginAccessIdentityCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateCloudFrontOriginAccessIdentityCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateCloudFrontOriginAccessIdentityCommandInput,
    UpdateCloudFrontOriginAccessIdentityCommandOutput
  >;
  private serialize;
  private deserialize;
}
